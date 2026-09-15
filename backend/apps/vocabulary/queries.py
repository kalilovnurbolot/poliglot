from django.db.models import Q

from .models import Word


def visible_words(user, language, level=None):
    """Words a user is allowed to see: system words (no owner) plus their own."""
    queryset = Word.objects.filter(language__code=language).filter(
        Q(owner__isnull=True) | Q(owner=user)
    )
    if level:
        queryset = queryset.filter(level=level)
    return queryset
