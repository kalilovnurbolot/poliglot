"""Speech recognition through the `voice` service (voice/server.py).

The browser records a phrase and POSTs it here as raw PCM; Django forwards it to the
voice service inside the Docker network. So the site needs no extra public address or
proxy rule for voice: it works wherever the site itself works, over HTTP or HTTPS.
"""

import hashlib
import hmac
import json
import time

from django.conf import settings
from django.urls import reverse
from websockets.exceptions import WebSocketException
from websockets.sync.client import connect

SAMPLE_RATE = 16000
MAX_SECONDS = 10
MAX_BYTES = SAMPLE_RATE * 2 * MAX_SECONDS
CHUNK_BYTES = SAMPLE_RATE * 2 // 4


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


def recognize(user, pcm, grammar=None):
    """Text of one phrase: `pcm` is mono 16 kHz signed 16-bit audio."""
    url = f'{settings.VOICE_SERVICE_URL}?token={voice_token(user)}'
    try:
        with connect(url, open_timeout=3, close_timeout=1) as ws:
            ws.send(json.dumps({'grammar': grammar}))
            for start in range(0, len(pcm), CHUNK_BYTES):
                ws.send(pcm[start:start + CHUNK_BYTES])
            ws.send(json.dumps({'eof': True}))
            texts = []
            while True:
                message = json.loads(ws.recv(timeout=10))
                if message.get('text'):
                    texts.append(message['text'])
                if message.get('final'):
                    return ' '.join(texts)
    except (OSError, TimeoutError, WebSocketException, ValueError) as e:
        raise VoiceUnavailable from e
