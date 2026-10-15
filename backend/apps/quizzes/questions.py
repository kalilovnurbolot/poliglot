import random

from apps.vocabulary.models import UserWordProgress
from apps.vocabulary.queries import visible_words

OPTION_COUNT = 4


class NotEnoughWords(Exception):
    pass


def build_questions(user, language, level=None, limit=10, deck=None):
    """Multiple-choice questions: a word plus a shuffled list of translation
    options (one correct, the rest random distractors). Words the user has
    already met are preferred, so the quiz checks what was actually learned."""
    pool = list(visible_words(user, language, level, deck))
    # A small group still makes a quiz: wrong options come from the whole language.
    distractor_source = list(visible_words(user, language)) if deck else pool
    if not pool:
        raise NotEnoughWords('Здесь пока нет слов.')
    if len(distractor_source) < OPTION_COUNT:
        raise NotEnoughWords('Недостаточно слов для квиза — сначала выучите ещё немного.')

    introduced_ids = set(
        UserWordProgress.objects.filter(user=user, word__in=pool)
        .values_list('word_id', flat=True)
    )
    introduced = [w for w in pool if w.id in introduced_ids]
    candidates = introduced if len(introduced) >= OPTION_COUNT else pool

    words = random.sample(candidates, k=min(limit, len(candidates)))

    questions = []
    for word in words:
        distractor_pool = [w for w in distractor_source if w.id != word.id]
        distractors = random.sample(distractor_pool, k=min(OPTION_COUNT - 1, len(distractor_pool)))
        options = [word.translation] + [d.translation for d in distractors]
        random.shuffle(options)
        questions.append({'word': word, 'options': options})
    return questions
