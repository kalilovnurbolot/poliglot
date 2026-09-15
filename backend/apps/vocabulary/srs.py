from datetime import timedelta

from django.utils import timezone

MAX_BOX_LEVEL = 7

BOX_INTERVALS = {
    0: timedelta(minutes=10),
    1: timedelta(hours=1),
    2: timedelta(hours=8),
    3: timedelta(days=1),
    4: timedelta(days=3),
    5: timedelta(days=7),
    6: timedelta(days=14),
    7: timedelta(days=30),
}

FAVORITE_REVIEW_DELAY = timedelta(hours=1)

SWIPE_DIRECTIONS = ('right', 'left', 'up', 'down')


def apply_swipe(progress, direction):
    """Update a UserWordProgress in place according to the swipe's meaning.

    right = knows it (SRS advances), left = doesn't know it (resets to box 0),
    up = mark as favorite/hard for extra practice without touching SRS counters,
    down = skip for now, no effect at all.
    """
    now = timezone.now()

    if direction == 'right':
        progress.box_level = min(progress.box_level + 1, MAX_BOX_LEVEL)
        progress.correct_count += 1
        progress.last_result = 'correct'
        progress.next_review_at = now + BOX_INTERVALS[progress.box_level]
    elif direction == 'left':
        progress.box_level = 0
        progress.wrong_count += 1
        progress.last_result = 'wrong'
        progress.next_review_at = now + BOX_INTERVALS[0]
    elif direction == 'up':
        progress.is_favorite = True
        progress.next_review_at = now + FAVORITE_REVIEW_DELAY
    elif direction == 'down':
        pass

    return progress
