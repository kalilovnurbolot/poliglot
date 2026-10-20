"""Speech recognition through the `voice` service (voice/server.py).

The browser records a phrase and POSTs it here as raw PCM; Django forwards it to the
voice service inside the Docker network. So the site needs no extra public address or
proxy rule for voice: it works wherever the site itself works, over HTTP or HTTPS.
"""

import hashlib
import hmac
import json
import re
import time

from django.conf import settings
from django.urls import reverse
from websockets.exceptions import WebSocketException
from websockets.sync.client import connect

SAMPLE_RATE = 16000
MAX_SECONDS = 10
MAX_BYTES = SAMPLE_RATE * 2 * MAX_SECONDS
CHUNK_BYTES = SAMPLE_RATE * 2 // 4
# Languages the voice service has models for (VOICE_LANGUAGES in voice/Dockerfile).
LANGUAGES = ('ru', 'en', 'de')
MAX_HINTS = 50
MAX_HINT_LENGTH = 100


class VoiceUnavailable(Exception):
    pass


def voice_token(user):
    """Short-lived token the voice service checks with the shared VOICE_SECRET."""
    payload = f'{user.pk}:{int(time.time())}'
    signature = hmac.new(settings.VOICE_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f'{payload}:{signature}'


def voice_config():
    """Settings for voice.js, or None to hide voice control."""
    if not settings.VOICE_SERVICE_URL:
        return None
    return {'url': reverse('web:voice-recognize')}


def clean_hints(hints):
    """Expected phrases as the voice service takes them: lowercase words, no punctuation."""
    cleaned = []
    for hint in hints:
        words = re.findall(r"[^\W_]+(?:'[^\W_]+)?", str(hint)[:MAX_HINT_LENGTH].lower().replace('’', "'"))
        if words and ' '.join(words) not in cleaned:
            cleaned.append(' '.join(words))
    return cleaned[:MAX_HINTS]


def recognize(user, pcm, grammar=None, language='ru', details=False, hints=None):
    """One phrase: `pcm` is mono 16 kHz signed 16-bit audio -> {"text": ...}.

    With `details` the result also has "words": [{"word", "conf", "start", "end"}] and keeps
    low-confidence words, so the caller can judge pronunciation itself. `hints` are the
    phrases the page expects; when one of them was clearly said but free recognition
    misheard it, the result has it as "alternative".
    """
    url = f'{settings.VOICE_SERVICE_URL}?token={voice_token(user)}'
    config = {'grammar': grammar, 'language': language, 'details': details}
    if hints:
        config['hints'] = clean_hints(hints)
    try:
        with connect(url, open_timeout=3, close_timeout=1) as ws:
            ws.send(json.dumps(config))
            for start in range(0, len(pcm), CHUNK_BYTES):
                ws.send(pcm[start:start + CHUNK_BYTES])
            ws.send(json.dumps({'eof': True}))
            texts = []
            while True:
                message = json.loads(ws.recv(timeout=10))
                if message.get('text'):
                    texts.append(message['text'])
                if message.get('final'):
                    result = {'text': ' '.join(texts)}
                    if details:
                        result['words'] = message.get('words', [])
                    if message.get('alternative'):
                        result['alternative'] = message['alternative']
                    return result
    except (OSError, TimeoutError, WebSocketException, ValueError) as e:
        raise VoiceUnavailable from e
