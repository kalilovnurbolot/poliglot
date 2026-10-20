"""Missions: role-play scenes where the player talks to a character (apps/missions).

The playthrough lives in the session: mission_play() starts it, every answer is posted
to mission_step(), which checks it against the current step (missions/scoring.py) and,
after the last step, saves a MissionAttempt with the scores.
"""

import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.missions.grammar_check import check_grammar
from apps.missions.meaning import meaning_match
from apps.missions.models import Mission, MissionAttempt, MissionStep
from apps.missions.scoring import evaluate_step, missing_keywords, says, normalize, summarize
from apps.users.activity import Action, log_activity
from apps.vocabulary.models import UserWordProgress, Word
from apps.vocabulary.srs import apply_swipe

from .context_processors import current_language
from .voice import voice_config

# After this many failed tries on a step the hint is shown and the step can be skipped.
HINT_AFTER_FAILS = 2
MAX_TEXT_LENGTH = 500
MAX_WORDS = 100
MAX_SOUND_TEXT = 100
# Map points (percent of the map) for missions without their own, along a winding road.
DEFAULT_MAP_POINTS = [(14, 78), (32, 60), (15, 25), (44, 22), (60, 48), (80, 72), (84, 24), (50, 86), (66, 14)]


def _session_key(mission):
    return f'mission:{mission.pk}'


def current_step(request, mission_id):
    """The step the player is answering in a started mission, for voice hints."""
    if not str(mission_id or '').isdigit():
        return None
    state = request.session.get(f'mission:{mission_id}')
    if state is None:
        return None
    return MissionStep.objects.filter(mission_id=mission_id).order_by('order')[state['step']:state['step'] + 1].first()


def step_hints(step, language):
    """What the player is expected to say: the sample answers and every keyword."""
    return [' '.join(normalize(p, language)) for p in step.patterns] + [k for group in step.keywords for k in group]


def prefer_expected(result, step, language):
    """The recognized text, or the hinted alternative when only that reaches the step's goal:
    free recognition of a small model often garbles an accent the hinted one gets right."""
    alternative = result.get('alternative')
    if alternative and missing_keywords(step, result['text'], language) and not missing_keywords(step, alternative, language):
        return alternative
    return result['text']


def _step_data(step):
    return {'order': step.order, 'npc_line': step.npc_line, 'npc_line_ru': step.npc_line_ru, 'goal': step.goal}


def _clean_words(raw):
    """Word details from the voice service, as posted back by the page."""
    if not isinstance(raw, list):
        return []
    words = []
    for w in raw[:MAX_WORDS]:
        try:
            words.append({'word': str(w['word'])[:50], 'conf': float(w['conf']), 'start': float(w['start']), 'end': float(w['end'])})
        except (KeyError, TypeError, ValueError):
            return []
    return words


def _clean_pronunciation(raw):
    """Sound-by-sound scores from the pronounce service, as posted back by the page."""
    if not isinstance(raw, dict) or not isinstance(raw.get('words'), list):
        return None
    words = []
    for w in raw['words'][:MAX_WORDS]:
        try:
            words.append({
                'word': str(w['word'])[:50],
                'expected': str(w['expected'])[:MAX_SOUND_TEXT],
                'heard': str(w['heard'])[:MAX_SOUND_TEXT],
                'score': min(1.0, max(0.0, float(w['score']))),
                'subs': [[str(a)[:8], str(b)[:8]] for a, b in w['subs'][:20]],
            })
        except (KeyError, TypeError, ValueError):
            return None
    return words or None


def _mission_map(user, language):
    """Published missions of a language in story order, each marked done / current / locked:
    a mission opens once the one before it was finished at least once."""
    items = list(
        Mission.objects.filter(language__code=language, is_published=True)
        .annotate(best_stars=Max('attempts__stars', filter=Q(attempts__user=user)))
    )
    previous_done = True
    for index, mission in enumerate(items):
        mission.chapter = index + 1
        mission.done = mission.best_stars is not None
        mission.locked = not previous_done
        mission.current = previous_done and not mission.done
        mission.previous = items[index - 1] if index else None
        default_x, default_y = DEFAULT_MAP_POINTS[index % len(DEFAULT_MAP_POINTS)]
        mission.x = default_x if mission.map_x is None else min(mission.map_x, 100)
        mission.y = default_y if mission.map_y is None else min(mission.map_y, 100)
        previous_done = mission.done
    return items


@login_required
def missions(request):
    items = _mission_map(request.user, current_language(request))
    # The road between the points (map viewBox is 400 x 300), walked part first.
    points = [(m.x * 4, m.y * 3) for m in items]
    walked = 1 + max((i for i, m in enumerate(items) if m.done), default=-1)
    return render(request, 'web/missions.html', {
        'missions': items,
        'selected': next((m for m in items if m.current), items[-1] if items else None),
        'road': ' '.join(f'{x},{y}' for x, y in points),
        'road_walked': ' '.join(f'{x},{y}' for x, y in points[:walked + 1]) if walked else '',
    })


@login_required
def mission_play(request, pk):
    mission = get_object_or_404(Mission.objects.select_related('language'), pk=pk, is_published=True)
    if next(m for m in _mission_map(request.user, mission.language.code) if m.pk == mission.pk).locked:
        return redirect('web:missions')
    steps = list(mission.steps.all())
    request.session[_session_key(mission)] = {
        'started': timezone.now().isoformat(), 'step': 0, 'fails': 0, 'answers': [], 'skipped': [],
    }
    language = mission.language.code
    voice = voice_config()
    if voice:
        voice['url'] += f'?language={language}&details=1&pronounce=1&mission={mission.pk}'
    config = {
        'language': language,
        'npcName': mission.npc_name,
        'targetWords': mission.target_words,
        'retryLine': mission.retry_line,
        'stepUrl': reverse('web:mission-step', args=[mission.pk]),
        'firstStep': _step_data(steps[0]) if steps else None,
        'stepCount': len(steps),
        'voice': voice,
    }
    return render(request, 'web/mission_play.html', {'mission': mission, 'config': config})


@login_required
@require_POST
def mission_step(request, pk):
    """{"text", "words", "pronunciation"} or {"skip": true} -> result of the answer and the next step."""
    mission = get_object_or_404(Mission.objects.select_related('language'), pk=pk, is_published=True)
    state = request.session.get(_session_key(mission))
    steps = list(mission.steps.all())
    if state is None or state['step'] >= len(steps):
        return JsonResponse({'detail': 'Миссия не начата.'}, status=400)
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({'detail': 'Некорректный запрос.'}, status=400)
    step = steps[state['step']]
    language = mission.language.code

    if data.get('skip'):
        if state['fails'] < HINT_AFTER_FAILS:
            return JsonResponse({'detail': 'Сначала попробуйте ответить.'}, status=400)
        state['skipped'].append(step.order)
        passed = True
        result = {'passed': False, 'missing': []}
    else:
        text = data.get('text')
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT_LENGTH:
            return JsonResponse({'detail': 'Пустой ответ.'}, status=400)
        text = text.strip()
        result = evaluate_step(
            step, text, _clean_words(data.get('words')), language,
            grammar=check_grammar(text, language), meaning=meaning_match(text, step, steps),
            sounds=_clean_pronunciation(data.get('pronunciation')),
        )
        state['answers'].append(result)
        passed = result['passed']

    if passed:
        state['step'] += 1
        state['fails'] = 0
    else:
        state['fails'] += 1
    request.session.modified = True

    spoken = normalize(' '.join(a['text'] for a in state['answers']), language)
    reply = {
        'passed': result['passed'],
        'missing': result['missing'],
        'usedWords': [w for w in mission.target_words if says(spoken, w, language)],
    }
    if state['step'] >= len(steps):
        attempt = _finish(request, mission, steps, state)
        reply.update(done=True, farewell=mission.farewell_line, resultUrl=reverse('web:mission-attempt', args=[attempt.pk]))
    elif passed:
        reply['next'] = _step_data(steps[state['step']])
    elif state['fails'] >= HINT_AFTER_FAILS:
        reply.update(hint=step.patterns[0] if step.patterns else '', canSkip=True)
    return JsonResponse(reply)


def _finish(request, mission, steps, state):
    summary = summarize(mission, steps, state['answers'], state['skipped'])
    attempt = MissionAttempt.objects.create(
        user=request.user,
        mission=mission,
        started_at=datetime.fromisoformat(state['started']),
        total=summary['total'],
        stars=summary['stars'],
        scores=summary['scores'],
        feedback=summary['feedback'],
        transcript=[
            {
                'goal': next(s.goal for s in steps if s.order == a['step']), 'text': a['text'], 'passed': a['passed'],
                'unclear': list(dict.fromkeys(a['unclear'] + a.get('mispronounced', []))), 'corrected': a.get('corrected'),
            }
            for a in state['answers']
        ],
    )
    # Target words said during the mission count as known in spaced repetition.
    if summary['used_words']:
        same_text = Q()
        for text in summary['used_words']:
            same_text |= Q(text__iexact=text)
        for word in Word.objects.filter(same_text, language=mission.language, owner__isnull=True):
            progress, _ = UserWordProgress.objects.get_or_create(user=request.user, word=word)
            apply_swipe(progress, 'right')
            progress.save()
    log_activity(request, Action.MISSION_COMPLETE, f'{mission.title} — {summary["total"]}')
    del request.session[_session_key(mission)]
    return attempt


SCORE_LABELS = [
    ('task', 'Выполнение задания'),
    ('words', 'Слова задания'),
    ('grammar', 'Построение фраз'),
    ('pronunciation', 'Произношение'),
    ('fluency', 'Беглость'),
]


@login_required
def mission_attempt(request, pk):
    attempt = get_object_or_404(MissionAttempt.objects.select_related('mission__language'), pk=pk, user=request.user)
    scores = [(label, attempt.scores.get(key)) for key, label in SCORE_LABELS]
    chapters = _mission_map(request.user, attempt.mission.language.code)
    return render(request, 'web/mission_result.html', {
        'attempt': attempt,
        'next_mission': next((m for m in chapters if m.previous and m.previous.pk == attempt.mission_id), None),
        'scores': scores,
        'unclear': list(dict.fromkeys(w for line in attempt.transcript for w in line['unclear'])),
    })
