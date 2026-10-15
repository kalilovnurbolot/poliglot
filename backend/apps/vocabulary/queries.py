from django.db.models import Q
from django.utils import timezone

from .models import UserWordProgress, Word


def visible_words(user, language, level=None):
    """Words a user is allowed to see: system words (no owner) plus their own."""
    queryset = Word.objects.filter(language__code=language).filter(
        Q(owner__isnull=True) | Q(owner=user)
    )
    if level:
        queryset = queryset.filter(level=level)
    return queryset


def review_queue(user, language, level=None, limit=20):
    """Words due for review right now, plus new words to fill up the batch."""
    words = visible_words(user, language, level)

    due_progress = list(
        UserWordProgress.objects.filter(
            user=user, word__in=words, next_review_at__lte=timezone.now(),
        )
        .select_related('word')
        .order_by('next_review_at')[:limit]
    )
    cards = [{'word': p.word, 'progress': p} for p in due_progress]

    remaining = limit - len(cards)
    if remaining > 0:
        new_words = (
            words.exclude(progress_entries__user=user)
            .order_by('text')[:remaining]
        )
        cards += [{'word': word, 'progress': None} for word in new_words]

    return cards
