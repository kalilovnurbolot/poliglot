import random

from apps.vocabulary.models import UserWordProgress
from apps.vocabulary.queries import visible_words

OPTION_COUNT = 4


class NotEnoughWords(Exception):
    pass


def build_questions(user, language, level=None, limit=10):
    """Multiple-choice questions: a word plus a shuffled list of translation
    options (one correct, the rest random distractors). Words the user has
    already met are preferred, so the quiz checks what was actually learned."""
    pool = list(visible_words(user, language, level))
    if len(pool) < OPTION_COUNT:
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
        distractor_pool = [w for w in pool if w.id != word.id]
        distractors = random.sample(distractor_pool, k=min(OPTION_COUNT - 1, len(distractor_pool)))
        options = [word.translation] + [d.translation for d in distractors]
        random.shuffle(options)
        questions.append({'word': word, 'options': options})
    return questions
