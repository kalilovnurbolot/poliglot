from django.db.models import Q
from django.utils import timezone

from .models import Deck, UserWordProgress, Word

DEFAULT_DECK_NAME = 'Мои слова'


def visible_words(user, language, level=None, deck=None):
    """Words a user is allowed to see: system words (no owner) plus their own."""
    queryset = Word.objects.filter(language__code=language).filter(
        Q(owner__isnull=True) | Q(owner=user)
    )
    if level:
        queryset = queryset.filter(level=level)
    if deck:
        queryset = queryset.filter(decks=deck)
    return queryset


def visible_decks(user):
    """System decks (topics) plus the user's own groups."""
    return Deck.objects.filter(Q(owner__isnull=True) | Q(owner=user))


def default_deck(user, language):
    """The user's «Мои слова» group for a language, created on first use."""
    deck, _ = Deck.objects.get_or_create(
        owner=user, language=language, is_default=True, defaults={'name': DEFAULT_DECK_NAME},
    )
    return deck


def user_decks(user, language):
    """The user's own groups for a language, «Мои слова» first."""
    default_deck(user, language)
    return Deck.objects.filter(owner=user, language=language).order_by('-is_default', 'name')


def review_queue(user, language, level=None, limit=20, deck=None):
    """Words due for review right now, plus new words to fill up the batch."""
    words = visible_words(user, language, level, deck)

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
