import json
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, Max, OuterRef
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.core.models import Language, Level
from apps.grammar.models import GrammarProgress, GrammarRule
from apps.quizzes.questions import NotEnoughWords, build_questions
from apps.quizzes.serializers import QuizQuestionSerializer
from apps.users.google import GoogleAuthError, user_from_google_token
from apps.vocabulary.models import Deck, Word
from apps.vocabulary.queries import review_queue, user_decks, visible_decks
from apps.vocabulary.serializers import ReviewCardSerializer

from .context_processors import SESSION_KEY, current_language
from .forms import GrammarRuleForm, LoginForm, RegisterForm, WordForm
from .rule_render import extract_lede, extract_sections, render_rule
from .voice import MAX_BYTES, VoiceUnavailable, recognize, voice_config

LEVELS = Level.values
STATIC_DIR = Path(__file__).resolve().parent / 'static' / 'web'

NEW_RULE_TEMPLATE = """```legend
s: подлежащее
v: глагол
o: дополнение
m: время / место
```

Коротко: когда и зачем используется это правило.

## Формула

```formula
+ | [s: Subject] + [v: Verb] + [o: Object]
```

```example
[s: I] [v: like] [o: coffee]
= Я люблю кофе.
```

```note
! | Частая ошибка и как её избежать.
```
"""


def _level_param(request, default=None):
    level = request.GET.get('level')
    return level if level in LEVELS else default


def _safe_next(request, fallback='/', target=None):
    target = target or request.POST.get('next') or request.GET.get('next')
    if target and url_has_allowed_host_and_scheme(target, {request.get_host()}, request.is_secure()):
        return target
    return fallback


# ---------- Home & settings ----------

def home(request):
    user = request.user
    display_name = (user.first_name or user.email.split('@')[0]) if user.is_authenticated else ''
    return render(request, 'web/home.html', {'display_name': display_name})


@require_POST
def set_language(request):
    code = request.POST.get('language')
    if Language.objects.filter(code=code).exists():
        request.session[SESSION_KEY] = code
    return redirect(_safe_next(request))


# ---------- Auth ----------

def login_view(request):
    form = LoginForm(request, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.user)
        return redirect(_safe_next(request))
    return render(request, 'web/login.html', {'form': form, 'next': _safe_next(request, '')})


def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('web:home')
    return render(request, 'web/register.html', {'form': form})


@require_POST
def google_login(request):
    try:
        data = json.loads(request.body)
        user = user_from_google_token(data.get('credential', ''))
        next_url = data.get('next')
        if not isinstance(next_url, str):
            next_url = ''
    except (ValueError, AttributeError):
        return JsonResponse({'detail': 'Некорректный запрос.'}, status=400)
    except GoogleAuthError as e:
        return JsonResponse({'detail': str(e)}, status=401)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({'ok': True, 'redirect': _safe_next(request, target=next_url)})


@require_POST
def logout_view(request):
    logout(request)
    return redirect('web:home')


# ---------- Words: flashcards & quiz ----------

def _word_sources(request, level_url, deck_url):
    """What learn and quiz start from: a level, the user's own groups or a topic deck."""
    language = get_object_or_404(Language, code=current_language(request))
    groups = list(user_decks(request.user, language).annotate(word_count=Count('words')))
    topics = list(
        Deck.objects.filter(owner__isnull=True, language=language)
        .annotate(word_count=Count('words')).filter(word_count__gt=0)
    )
    for deck in groups + topics:
        deck.url = deck_url(deck.pk)
    return {
        'level_links': [('Все уровни', level_url('all'))] + [(l, level_url(l)) for l in LEVELS],
        'groups': groups,
        'topics': topics,
    }


def _visible_deck(request, pk):
    return get_object_or_404(visible_decks(request.user).select_related('language'), pk=pk)


@login_required
def learn(request):
    return render(request, 'web/learn.html', _word_sources(
        request,
        level_url=lambda level: reverse('web:learn-session', args=[level]),
        deck_url=lambda pk: reverse('web:learn-deck', args=[pk]),
    ))


def _learn_session(request, cards):
    return render(request, 'web/learn_session.html', {
        'cards': ReviewCardSerializer(cards, many=True).data,
        'voice': voice_config(),
    })


@login_required
def learn_session(request, level):
    if level != 'all' and level not in LEVELS:
        raise Http404
    return _learn_session(request, review_queue(
        request.user, current_language(request), None if level == 'all' else level,
    ))


@login_required
def learn_deck(request, pk):
    deck = _visible_deck(request, pk)
    return _learn_session(request, review_queue(request.user, deck.language.code, deck=deck))


@login_required
@require_POST
def voice_recognize(request):
    """One recorded phrase (raw 16 kHz 16-bit PCM in the body) -> {"text": ...}."""
    if voice_config() is None:
        raise Http404
    pcm = request.body
    if not pcm or len(pcm) > MAX_BYTES or len(pcm) % 2:
        return JsonResponse({'detail': 'Некорректная запись.'}, status=400)
    try:
        text = recognize(request.user, pcm)
    except VoiceUnavailable:
        return JsonResponse({'detail': 'Сервис распознавания речи недоступен.'}, status=503)
    return JsonResponse({'text': text})


@login_required
def quiz(request):
    mode = 'listening' if request.GET.get('mode') == 'listening' else 'translation'
    deck_id = request.GET.get('deck')
    level = request.GET.get('level')
    if deck_id is None and level != 'all' and level not in LEVELS:
        mode_param = '&mode=listening' if mode == 'listening' else ''
        return render(request, 'web/quiz_pick.html', _word_sources(
            request,
            level_url=lambda l: f'?level={l}{mode_param}',
            deck_url=lambda pk: f'?deck={pk}{mode_param}',
        ))

    if deck_id is not None:
        if not deck_id.isdigit():
            raise Http404
        deck = _visible_deck(request, deck_id)
        language, level, source = deck.language.code, None, deck.name
    else:
        deck, language = None, current_language(request)
        source = 'Все уровни' if level == 'all' else f'Уровень {level}'
        level = None if level == 'all' else level

    error = None
    questions = []
    try:
        questions = QuizQuestionSerializer(
            build_questions(request.user, language, level, deck=deck), many=True,
        ).data
    except NotEnoughWords as e:
        error = str(e)
    return render(request, 'web/quiz.html', {
        'source': source,
        'mode': mode,
        'questions': questions,
        'error': error,
    })


@login_required
def words(request):
    language = get_object_or_404(Language, code=current_language(request))
    level = _level_param(request)
    groups = user_decks(request.user, language)
    deck_id = request.GET.get('deck')
    deck = groups.filter(pk=deck_id).first() if deck_id and deck_id.isdigit() else None

    form = WordForm(request.POST or None, decks=groups, initial={'deck': deck or groups.first()})
    if request.method == 'POST' and form.is_valid():
        form.instance.owner = request.user
        form.instance.language = language
        word = form.save()
        word.decks.set([form.cleaned_data['deck']])
        return redirect(request.get_full_path())

    my_words = (
        Word.objects.filter(owner=request.user, language=language)
        .prefetch_related('decks').order_by('-created_at')
    )
    if deck:
        my_words = my_words.filter(decks=deck)
    if level:
        my_words = my_words.filter(level=level)

    return render(request, 'web/words.html', {
        'form': form,
        'words': my_words,
        'groups': groups.annotate(word_count=Count('words')),
        'deck': deck,
        'deck_param': f'&deck={deck.pk}' if deck else '',
        'levels': LEVELS,
        'level': level,
    })


@login_required
@require_POST
def group_create(request):
    language = get_object_or_404(Language, code=current_language(request))
    name = request.POST.get('name', '').strip()[:100]
    if not name:
        return redirect('web:words')
    deck, _ = Deck.objects.get_or_create(owner=request.user, language=language, name=name)
    return redirect(f"{reverse('web:words')}?deck={deck.pk}")


@login_required
@require_POST
def word_delete(request, pk):
    word = get_object_or_404(Word, pk=pk, owner=request.user)
    word.delete()
    return redirect(_safe_next(request, reverse('web:words')))


# ---------- Grammar ----------

def _rules_for(request, language, level):
    rules = GrammarRule.objects.filter(language__code=language, level=level)
    if request.user.is_authenticated:
        rules = rules.annotate(is_learned=Exists(
            GrammarProgress.objects.filter(user=request.user, rule=OuterRef('pk'))
        ))
    return list(rules)


def grammar_list(request):
    level = _level_param(request, 'A1')
    rules = _rules_for(request, current_language(request), level)
    for rule in rules:
        rule.lede = extract_lede(rule.body)
    learned_count = sum(1 for r in rules if getattr(r, 'is_learned', False))
    return render(request, 'web/grammar_list.html', {
        'levels': LEVELS,
        'level': level,
        'rules': rules,
        'learned_count': learned_count,
        'learned_percent': round(learned_count / len(rules) * 100) if rules else 0,
    })


def grammar_detail(request, pk):
    rule = get_object_or_404(GrammarRule.objects.select_related('language'), pk=pk)
    siblings = _rules_for(request, rule.language.code, rule.level)
    ids = [r.id for r in siblings]
    index = ids.index(rule.id)
    rule.is_learned = getattr(siblings[index], 'is_learned', False)
    return render(request, 'web/grammar_detail.html', {
        'rule': rule,
        'body_html': render_rule(rule.body),
        'sections': extract_sections(rule.body),
        'position': index + 1,
        'total': len(siblings),
        'prev': siblings[index - 1] if index > 0 else None,
        'next': siblings[index + 1] if index < len(siblings) - 1 else None,
    })


@login_required
@require_POST
def grammar_toggle_learned(request, pk):
    rule = get_object_or_404(GrammarRule, pk=pk)
    progress, created = GrammarProgress.objects.get_or_create(user=request.user, rule=rule)
    if not created:
        progress.delete()
    return redirect('web:grammar-detail', pk=pk)


def _staff_only(request):
    return render(request, 'web/staff_only.html', status=403)


@login_required
def grammar_create(request):
    if not request.user.is_staff:
        return _staff_only(request)
    language = get_object_or_404(Language, code=current_language(request))
    form = GrammarRuleForm(request.POST or None, initial={'level': 'A1', 'body': NEW_RULE_TEMPLATE})
    if request.method == 'POST' and form.is_valid():
        # New rules go to the end of their level instead of jumping ahead of the system ones.
        last_order = GrammarRule.objects.filter(
            language=language, level=form.cleaned_data['level'],
        ).aggregate(Max('order'))['order__max'] or 0
        form.instance.language = language
        form.instance.order = last_order + 1
        rule = form.save()
        return redirect('web:grammar-detail', pk=rule.pk)
    return render(request, 'web/grammar_form.html', {
        'form': form,
        'title': 'Новое правило',
        'submit_label': 'Добавить правило',
        'back_url': reverse('web:grammar'),
        'back_label': '← Все правила',
        'preview_html': render_rule(form['body'].value() or ''),
    })


@login_required
def grammar_edit(request, pk):
    if not request.user.is_staff:
        return _staff_only(request)
    rule = get_object_or_404(GrammarRule, pk=pk)
    form = GrammarRuleForm(request.POST or None, instance=rule)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('web:grammar-detail', pk=rule.pk)
    return render(request, 'web/grammar_form.html', {
        'form': form,
        'title': 'Редактирование правила',
        'submit_label': 'Сохранить',
        'back_url': reverse('web:grammar-detail', args=[rule.pk]),
        'back_label': '← К правилу',
        'preview_html': render_rule(form['body'].value() or ''),
    })


@login_required
@require_POST
def grammar_delete(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    rule = get_object_or_404(GrammarRule, pk=pk)
    rule.delete()
    messages.success(request, f'Правило «{rule.title}» удалено.')
    return redirect('web:grammar')


@login_required
@require_POST
def grammar_preview(request):
    """Live preview for the rule editor: Markdown body in, rendered HTML out."""
    if not request.user.is_staff:
        return HttpResponseForbidden()
    return HttpResponse(render_rule(request.POST.get('body', '')))


# ---------- PWA ----------

def manifest(request):
    return JsonResponse({
        'name': 'Полиглот',
        'short_name': 'Полиглот',
        'description': 'Учи английский и немецкий: слова свайпами, грамматика и квизы для начинающих.',
        'start_url': '/',
        'display': 'standalone',
        'background_color': '#fafafa',
        'theme_color': '#4f46e5',
        'lang': 'ru',
        'icons': [
            {'src': static('web/icons/icon-192.png'), 'sizes': '192x192', 'type': 'image/png'},
            {'src': static('web/icons/icon-512.png'), 'sizes': '512x512', 'type': 'image/png'},
        ],
    }, content_type='application/manifest+json', json_dumps_params={'ensure_ascii': False})


def service_worker(request):
    """Served from the site root (not /static/) so the worker's scope covers every page."""
    response = HttpResponse((STATIC_DIR / 'js' / 'sw.js').read_text(), content_type='application/javascript')
    response['Cache-Control'] = 'no-cache'
    return response
