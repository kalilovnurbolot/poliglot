"""Scoring of mission answers without any language model.

evaluate_step() checks one recognized phrase against the step: the goal is reached when
every keyword group was said, or, with the meaning service (meaning.py), when the phrase
means the same as the step's sample answers and clearly not what other steps ask for; sentence building is how close the phrase is to the
closest sample answer, minus the mistakes found by the grammar service (grammar_check.py)
when it is on. With word details from the voice service (conf, start, end)
it also measures fluency (pauses, pace) and pronunciation: sound by sound when the
pronounce service scored the recording (pronunciation.py), else by recognition confidence.
summarize() turns the answers of a playthrough into scores 0..100, stars and advice.
"""

import re
from difflib import SequenceMatcher
from statistics import mean

# Words the recognizer heard with less confidence are reported as unclear.
UNCLEAR_CONFIDENCE = 0.7
LONG_PAUSE_SECONDS = 0.8
SLOW_WORDS_PER_MINUTE = 60
# A phrase this close to a sample answer counts as well built.
GOOD_SIMILARITY = 0.8
# An answer without the keywords still reaches the goal when it is this close in meaning
# to the step's samples and this much closer to them than to other steps' samples.
MEANING_MIN = 0.8
MEANING_MARGIN = 0.15
# Nearly the same meaning only has to be closer to its own step than to the others.
MEANING_SURE = 0.9
# A word whose sounds were this right or less is reported as mispronounced.
MISPRONOUNCED = 0.75
# Advice for the sound that should have been there (Russian speakers' usual swaps).
SOUND_TIPS = {
    'θ': 'th в «think», «thank» — кончик языка между зубами, не «с» и не «ф».',
    'ð': 'th в «this», «the» — как в «think», но с голосом, не «з» и не «д».',
    'w': 'w — губы трубочкой, зубы губ не касаются (не «в»).',
    'v': 'v — верхние зубы касаются нижней губы (не w).',
    'æ': 'æ в «can», «have» — рот шире, звук между «а» и «э».',
    'iː': 'долгое «ии» в «please», «cheese» — тяните звук.',
    'ɪ': 'краткое «и» в «it», «think» — короче и открытее русского «и».',
    'r': 'английский r — язык не вибрирует, кончик чуть загнут назад.',
    'h': 'h — лёгкий выдох, не русское «х».',
    'ŋ': 'ŋ в «-ing», «thank» — задняя часть языка к нёбу, без «г» на конце.',
    'z': 'звонкое z на конце («please», «is») — не оглушайте до «с».',
    'd': 'звонкое d на конце («bread», «good») — не оглушайте до «т».',
    'ç': 'ich-Laut в «ich», «möchte» — тихое «хь», не «ш».',
    'œ': 'ö в «möchte» — губы как для «о», язык как для «э».',
    'y': 'ü в «für», «Tschüss» — губы как для «у», язык как для «и».',
}
# Points of the sentence-building score lost per grammar mistake.
GRAMMAR_ERROR_PENALTY = 15
WEIGHTS = {'task': 0.3, 'words': 0.2, 'grammar': 0.2, 'pronunciation': 0.15, 'fluency': 0.15}
STARS = [(85, 3), (65, 2), (40, 1)]

CONTRACTIONS = {
    'en': {
        "i'm": 'i am', "i'd": 'i would', "i'll": 'i will', "i've": 'i have', "it's": 'it is',
        "that's": 'that is', "what's": 'what is', "there's": 'there is', "you're": 'you are',
        "don't": 'do not', "doesn't": 'does not', "can't": 'can not', 'cannot': 'can not',
        "won't": 'will not', "isn't": 'is not', "we'd": 'we would', "we'll": 'we will',
    },
}


def normalize(text, language):
    """Lowercase words without punctuation, contractions expanded: "I'd like it!" -> [i, would, like, it]."""
    text = text.lower().replace('’', "'")
    words = re.findall(r"[\w']+", text)
    contractions = CONTRACTIONS.get(language, {})
    return ' '.join(contractions.get(w, w) for w in words).split()


def says(tokens, phrase, language):
    """Whether `phrase` (one or more words) occurs in `tokens` as whole words."""
    return f" {' '.join(normalize(phrase, language))} " in f" {' '.join(tokens)} "


def missing_keywords(step, text, language):
    """First word of each keyword group of `step` that `text` does not say."""
    tokens = normalize(text, language)
    return [group[0] for group in step.keywords if not any(says(tokens, k, language) for k in group)]


def evaluate_step(step, text, words, language, grammar=None, meaning=None, sounds=None):
    """One answer to a MissionStep. `words` are the voice service's word details or [],
    `grammar` the result of grammar_check.check_grammar(), `meaning` of
    meaning.meaning_match() and `sounds` the words of pronunciation.score_pronunciation(),
    each None when not checked."""
    tokens = normalize(text, language)
    missing = missing_keywords(step, text, language)

    best_pattern, similarity = '', 0.0
    for pattern in step.patterns:
        ratio = SequenceMatcher(None, tokens, normalize(pattern, language)).ratio()
        if ratio > similarity:
            best_pattern, similarity = pattern, ratio

    same_meaning = bool(meaning) and (
        meaning['own'] >= MEANING_MIN and meaning['own'] - meaning['other'] >= MEANING_MARGIN
        or meaning['own'] >= MEANING_SURE and meaning['own'] > meaning['other']
    )
    result = {
        'step': step.order,
        'text': text,
        'passed': bool(tokens) and (not missing or same_meaning),
        'missing': missing,
        'similarity': round(similarity, 2),
        'best_pattern': best_pattern,
        'meaning': meaning['own'] if meaning else None,
        'confidence': None,
        'unclear': [],
        'pauses': 0,
        'wpm': None,
        'grammar_errors': grammar['errors'] if grammar else None,
        'corrected': grammar['corrected'] if grammar and grammar['errors'] else None,
        'sounds': sounds,
        'mispronounced': [w['word'] for w in sounds if w['score'] <= MISPRONOUNCED] if sounds else [],
    }
    if words:
        result['confidence'] = round(mean(w['conf'] for w in words), 3)
        result['unclear'] = [w['word'] for w in words if w['conf'] < UNCLEAR_CONFIDENCE]
        result['pauses'] = sum(1 for a, b in zip(words, words[1:]) if b['start'] - a['end'] > LONG_PAUSE_SECONDS)
        duration = words[-1]['end'] - words[0]['start']
        if len(words) > 1 and duration > 0:
            result['wpm'] = round(len(words) / duration * 60)
    return result


def _built(answer):
    """How well an answer is built, 0..1: close to a sample answer word by word, or a
    whole phrase (not a lone word) meaning the same."""
    if (answer.get('meaning') or 0) >= MEANING_MIN and len(answer['text'].split()) >= 3:
        return 1
    return min(1, answer['similarity'] / GOOD_SIMILARITY)


def _clamp(value):
    return max(0, min(100, round(value)))


def summarize(mission, steps, answers, skipped=()):
    """Scores of a playthrough: `answers` are evaluate_step() results in order, `skipped`
    the orders of steps the player gave up on."""
    passed = {a['step']: a for a in answers if a['passed']}
    retries = len(answers) - len(passed)
    language = mission.language.code

    all_tokens = normalize(' '.join(a['text'] for a in answers), language)
    used = [w for w in mission.target_words if says(all_tokens, w, language)]
    missing_words = [w for w in mission.target_words if w not in used]

    voiced = [a for a in answers if a['confidence'] is not None]
    sounded = [w for a in answers for w in a.get('sounds') or []]
    pronunciation = None
    if sounded:
        pronunciation = _clamp(mean(w['score'] for w in sounded) * 100)
    elif voiced:
        # Confidence 0.5 or less is as good as not understood, 1.0 is perfectly clear.
        pronunciation = _clamp((mean(a['confidence'] for a in voiced) - 0.5) / 0.5 * 100)

    fluency = 100 - 10 * retries - 5 * sum(a['pauses'] for a in answers)
    paces = [a['wpm'] for a in voiced if a['wpm']]
    if paces and mean(paces) < SLOW_WORDS_PER_MINUTE:
        fluency -= SLOW_WORDS_PER_MINUTE - mean(paces)

    grammar_errors = sum(len(a.get('grammar_errors') or []) for a in answers)
    built = mean(_built(a) for a in passed.values()) * 100 if passed else 0
    scores = {
        'task': _clamp(100 * len(passed) / len(steps)) if steps else 0,
        'words': _clamp(100 * len(used) / len(mission.target_words)) if mission.target_words else 100,
        'grammar': _clamp(built - GRAMMAR_ERROR_PENALTY * grammar_errors) if passed else 0,
        'pronunciation': pronunciation,
        'fluency': _clamp(fluency),
    }
    weights = {k: w for k, w in WEIGHTS.items() if scores[k] is not None}
    total = _clamp(sum(scores[k] * w for k, w in weights.items()) / sum(weights.values()))
    stars = next((s for threshold, s in STARS if total >= threshold), 0)

    feedback = []
    goals = {s.order: s.goal for s in steps}
    for order in skipped:
        feedback.append(f'Пропущен шаг: {goals.get(order, order)}.')
    if missing_words:
        feedback.append(f'Не прозвучали слова задания: {", ".join(missing_words)}.')
    for a in answers:
        if a.get('corrected'):
            feedback.append(f'Ошибка: «{a["text"]}» → «{a["corrected"]}».')
    for a in passed.values():
        if a.get('corrected'):
            continue
        if _built(a) < 0.75 and a['best_pattern']:
            feedback.append(f'«{a["text"]}» — можно сказать полнее: «{a["best_pattern"]}».')
    # Answers scored sound by sound get exact advice instead of "unclear" words.
    unclear = list(dict.fromkeys(w for a in answers if not a.get('sounds') for w in a['unclear']))
    if unclear:
        feedback.append(f'Произнесите чётче: {", ".join(unclear[:6])}.')
    worst = {}
    for w in sorted(sounded, key=lambda w: w['score']):
        if w['score'] <= MISPRONOUNCED and w['word'] not in worst:
            worst[w['word']] = w
    for w in list(worst.values())[:5]:
        feedback.append(f'Произношение «{w["word"]}»: нужно [{w["expected"]}], прозвучало [{w["heard"]}].')
    tips = dict.fromkeys(SOUND_TIPS[want] for w in worst.values() for want, _ in w['subs'] if want in SOUND_TIPS)
    feedback.extend(list(tips)[:3])
    if retries:
        times = 'раза' if retries % 10 in (2, 3, 4) and retries % 100 not in (12, 13, 14) else 'раз'
        feedback.append(f'Собеседник переспрашивал {retries} {times}.')
    if not feedback:
        feedback.append('Отлично! Вы справились без единой ошибки.')

    unclear = list(dict.fromkeys(unclear + list(worst)))
    return {'total': total, 'stars': stars, 'scores': scores, 'feedback': feedback, 'unclear': unclear[:6], 'used_words': used}
