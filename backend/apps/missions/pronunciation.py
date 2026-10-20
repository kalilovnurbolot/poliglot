"""Pronunciation of a recorded answer, sound by sound, through the `pronounce` service
(pronounce/server.py): for each recognized word, how it should sound, how it sounded
and which sounds were replaced or dropped.
"""

import json
import logging
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

log = logging.getLogger(__name__)

# A phrase takes well under a second; the first one after the service starts is slower.
TIMEOUT_SECONDS = 15


def score_pronunciation(pcm, text, language):
    """{"score": 0..1, "words": [{"word", "expected", "heard", "score", "subs"}]}, or None
    when the service is off or did not answer."""
    if not settings.PRONOUNCE_SERVICE_URL or not text:
        return None
    query = urlencode({'language': language, 'text': text})
    request = Request(
        f'{settings.PRONOUNCE_SERVICE_URL.rstrip("/")}/score?{query}', pcm,
        {'Content-Type': 'application/octet-stream'},
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as res:
            return json.load(res)
    except (OSError, URLError, ValueError) as e:
        log.warning('pronounce service unavailable: %s', e)
        return None
