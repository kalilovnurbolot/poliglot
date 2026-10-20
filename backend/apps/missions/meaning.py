"""Meaning of a player's answer through the `meaning` service (meaning/server.py).

Phrases become unit vectors, so the dot product of two of them is how close their
meanings are (-1..1). An answer is compared with the sample answers of its own step and
with those of the mission's other steps: "can I have some milk" is close to "can I have
some bread" too, so only an answer clearly closer to its own step counts (scoring.py).
"""

import json
import logging
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings

log = logging.getLogger(__name__)

TIMEOUT_SECONDS = 5
# Vectors of sample answers are asked once per process; the cache is small anyway.
MAX_CACHED = 5000
_cache = {}


def _vectors(texts):
    missing = list(dict.fromkeys(t for t in texts if t not in _cache))
    if missing:
        request = Request(
            f'{settings.MEANING_SERVICE_URL.rstrip("/")}/embed',
            json.dumps({'texts': missing}).encode(),
            {'Content-Type': 'application/json'},
        )
        with urlopen(request, timeout=TIMEOUT_SECONDS) as res:
            vectors = json.load(res)['vectors']
        if len(_cache) + len(missing) > MAX_CACHED:
            _cache.clear()
        _cache.update(zip(missing, vectors))
    return [_cache[t] for t in texts]


def _closeness(a, b):
    return sum(x * y for x, y in zip(a, b))


def meaning_match(text, step, steps):
    """{"own": closeness to the step's samples, "other": to other steps' samples},
    or None when the service is off or did not answer."""
    if not settings.MEANING_SERVICE_URL or not step.patterns:
        return None
    others = [p for s in steps if s.pk != step.pk for p in s.patterns]
    try:
        answer, *samples = _vectors([text, *step.patterns, *others])
    except (OSError, URLError, ValueError, KeyError) as e:
        log.warning('meaning service unavailable: %s', e)
        return None
    own = samples[:len(step.patterns)]
    other = samples[len(step.patterns):]
    return {
        'own': round(max(_closeness(answer, v) for v in own), 3),
        'other': round(max((_closeness(answer, v) for v in other), default=0), 3),
    }
