"""Speech recognition service: a WebSocket server around a Vosk model.

Its only client is Django (apps/web/voice.py), inside the Docker network; browsers
send recorded phrases to Django over plain HTTPS.

Protocol (one connection = one listening session):
  1. The client connects to ws://<host>/?token=<signed token from Django>.
  2. Optionally it sends a JSON text message {"grammar": ["знаю", "не знаю", ...]};
     recognition is then limited to these phrases (much more accurate for commands).
     {"grammar": null} (or no message) means free speech, e.g. answers to check.
  3. Then it streams raw audio as binary messages: mono 16 kHz signed 16-bit PCM.
  4. After each pause in speech the server replies {"text": "<recognized phrase>"}.
  5. {"eof": true} finishes the current phrase: the server replies with what is left
     as {"text": "...", "final": true}.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
from urllib.parse import parse_qs, urlparse

from vosk import KaldiRecognizer, Model, SetLogLevel
from websockets.asyncio.server import serve

SAMPLE_RATE = 16000
MODEL_PATH = os.environ.get('VOICE_MODEL_PATH', '/models/ru')
SECRET = os.environ.get('VOICE_SECRET', '')
TOKEN_MAX_AGE = 60 * 60
SESSION_MAX_SECONDS = 15 * 60
MAX_MESSAGE_BYTES = 64 * 1024
# With a grammar Vosk maps any speech to the closest phrase ("привет как дела" -> "перевод"),
# so phrases with unknown or low-confidence words are dropped as noise. Free speech is
# checked by the page itself (e.g. against the expected answer), so it gets a softer cut.
MIN_WORD_CONFIDENCE = {'grammar': 0.7, 'free': 0.5}

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('voice')


def token_is_valid(token):
    """Tokens are '<user_id>:<timestamp>:<hmac>' signed by Django with the shared VOICE_SECRET."""
    if not SECRET:
        return True
    try:
        user_id, ts, signature = token.split(':')
        age = time.time() - int(ts)
    except ValueError:
        return False
    expected = hmac.new(SECRET.encode(), f'{user_id}:{ts}'.encode(), hashlib.sha256).hexdigest()
    return 0 <= age <= TOKEN_MAX_AGE and hmac.compare_digest(signature, expected)


def make_recognizer(model, grammar):
    """Returns (recognizer, min word confidence). No grammar = free speech."""
    if grammar:
        phrases = [p for p in grammar if isinstance(p, str)][:200]
        recognizer = KaldiRecognizer(model, SAMPLE_RATE, json.dumps(phrases + ['[unk]'], ensure_ascii=False))
        min_confidence = MIN_WORD_CONFIDENCE['grammar']
    else:
        recognizer = KaldiRecognizer(model, SAMPLE_RATE)
        min_confidence = MIN_WORD_CONFIDENCE['free']
    recognizer.SetWords(True)
    return recognizer, min_confidence


def confident_text(result, min_confidence):
    words = json.loads(result).get('result', [])
    if any(w['word'] == '[unk]' or w['conf'] < min_confidence for w in words):
        return ''
    return ' '.join(w['word'] for w in words)


def handler_for(model):
    async def handler(ws):
        query = parse_qs(urlparse(ws.request.path).query)
        if not token_is_valid(query.get('token', [''])[0]):
            await ws.close(4401, 'invalid token')
            return

        loop = asyncio.get_running_loop()
        recognizer = None
        deadline = loop.time() + SESSION_MAX_SECONDS

        async for message in ws:
            if loop.time() > deadline:
                await ws.close(4408, 'session too long')
                return
            if isinstance(message, str):
                try:
                    config = json.loads(message)
                except ValueError:
                    continue
                if config.get('eof'):
                    text = confident_text(recognizer.FinalResult(), min_confidence) if recognizer else ''
                    await ws.send(json.dumps({'text': text, 'final': True}, ensure_ascii=False))
                    continue
                recognizer, min_confidence = make_recognizer(model, config.get('grammar'))
                continue

            if recognizer is None:
                recognizer, min_confidence = make_recognizer(model, None)
            # Decoding is CPU-bound; keep the event loop free for other connections.
            if await loop.run_in_executor(None, recognizer.AcceptWaveform, message):
                text = confident_text(recognizer.Result(), min_confidence)
                if text:
                    await ws.send(json.dumps({'text': text}, ensure_ascii=False))

    return handler


async def main():
    SetLogLevel(-1)
    log.info('loading model from %s', MODEL_PATH)
    model = Model(MODEL_PATH)
    if not SECRET:
        log.warning('VOICE_SECRET is not set: connections are not authenticated')
    port = int(os.environ.get('VOICE_PORT', '2700'))
    async with serve(handler_for(model), '0.0.0.0', port, max_size=MAX_MESSAGE_BYTES):
        log.info('listening on :%s', port)
        await asyncio.get_running_loop().create_future()


if __name__ == '__main__':
    asyncio.run(main())
