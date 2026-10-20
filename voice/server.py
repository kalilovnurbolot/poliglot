"""Speech recognition service: a WebSocket server around a Vosk model.

Its only client is Django (apps/web/voice.py), inside the Docker network; browsers
send recorded phrases to Django over plain HTTPS.

Protocol (one connection = one listening session):
  1. The client connects to ws://<host>/?token=<signed token from Django>.
  2. Optionally it sends a JSON text message {"grammar": ["знаю", "не знаю", ...]};
     recognition is then limited to these phrases (much more accurate for commands).
     {"grammar": null} (or no message) means free speech, e.g. answers to check.
     The same message may set "language" (a code from VOICE_LANGUAGES, default the
     first one) and "details": true, for which nothing is dropped as noise and the final
     reply also carries "words": [{"word", "conf", "start", "end"}, ...] of the phrase
     (used to score pronunciation and fluency in missions).
     "hints": ["phrase", ...] are answers the page expects. The audio is then also
     decoded limited to them, and if that is confident, the final reply carries it as
     "alternative": small models often mishear a learner's accent in free speech, while
     the expected phrase, when it really was said, comes out of the limited decoder cleanly.
     The alternative is only a candidate answer: it is never a command (any speech maps
     to the closest hint, "грязный" may come out as "знаю").
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
from difflib import SequenceMatcher
from urllib.parse import parse_qs, urlparse

from vosk import KaldiRecognizer, Model, SetLogLevel
from websockets.asyncio.server import serve

SAMPLE_RATE = 16000
MODELS_DIR = os.environ.get('VOICE_MODELS_DIR', '/models')
# Each language is a Vosk model in MODELS_DIR/<code>; the first one is the default.
LANGUAGES = [code for code in os.environ.get('VOICE_LANGUAGES', 'ru,en,de').split(',') if code]
SECRET = os.environ.get('VOICE_SECRET', '')
TOKEN_MAX_AGE = 60 * 60
SESSION_MAX_SECONDS = 15 * 60
MAX_MESSAGE_BYTES = 64 * 1024
# With a grammar Vosk maps any speech to the closest phrase ("привет как дела" -> "перевод"),
# so phrases with unknown or low-confidence words are dropped as noise. Free speech is
# checked by the page itself (e.g. against the expected answer), so it gets a softer cut.
MIN_WORD_CONFIDENCE = {'grammar': 0.7, 'free': 0.5}
# Hints map any speech to the closest expected phrase too, so their cut is the strictest.
HINT_CONFIDENCE = 0.85
# ...and it must sound like what free recognition heard, unless that heard nothing sure:
# "whereas cafe marina" -> "where is cafe luna" is kept, "рыба" -> "радуга" is not.
HINT_SIMILARITY = 0.5
MAX_HINTS = 200

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


def make_recognizer(model, grammar, details=False):
    """Returns (recognizer, min word confidence). No grammar = free speech."""
    if details:
        recognizer = KaldiRecognizer(model, SAMPLE_RATE)
        min_confidence = 0
    elif grammar:
        phrases = [p for p in grammar if isinstance(p, str)][:200]
        recognizer = KaldiRecognizer(model, SAMPLE_RATE, json.dumps(phrases + ['[unk]'], ensure_ascii=False))
        min_confidence = MIN_WORD_CONFIDENCE['grammar']
    else:
        recognizer = KaldiRecognizer(model, SAMPLE_RATE)
        min_confidence = MIN_WORD_CONFIDENCE['free']
    recognizer.SetWords(True)
    return recognizer, min_confidence


def make_hint_recognizer(model, hints):
    phrases = [p.strip().lower() for p in hints if isinstance(p, str) and p.strip()][:MAX_HINTS]
    if not phrases:
        return None
    recognizer = KaldiRecognizer(model, SAMPLE_RATE, json.dumps(phrases + ['[unk]'], ensure_ascii=False))
    recognizer.SetWords(True)
    return recognizer


def hint_text(results):
    """The phrase the hint decoder heard over all its results, or '' if any part is unsure."""
    words = [w for result in results for w in json.loads(result).get('result', [])]
    if not words or any(w['word'] == '[unk]' or w['conf'] < HINT_CONFIDENCE for w in words):
        return ''
    return ' '.join(w['word'] for w in words)


def confident_text(result, min_confidence):
    words = json.loads(result).get('result', [])
    if any(w['word'] == '[unk]' or w['conf'] < min_confidence for w in words):
        return ''
    return ' '.join(w['word'] for w in words)


def result_words(result):
    return [
        {'word': w['word'], 'conf': round(w['conf'], 3), 'start': round(w['start'], 2), 'end': round(w['end'], 2)}
        for w in json.loads(result).get('result', []) if w['word'] != '[unk]'
    ]


def handler_for(models):
    async def handler(ws):
        query = parse_qs(urlparse(ws.request.path).query)
        if not token_is_valid(query.get('token', [''])[0]):
            await ws.close(4401, 'invalid token')
            return

        loop = asyncio.get_running_loop()
        recognizer = hint_recognizer = None
        language, details, words, hint_results = LANGUAGES[0], False, [], []
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
                    reply = {'final': True}
                    if recognizer is None:
                        reply['text'] = sure = ''
                    elif details:
                        words += result_words(recognizer.FinalResult())
                        reply.update(text=' '.join(w['word'] for w in words), words=words)
                        unsure = any(w['conf'] < MIN_WORD_CONFIDENCE['free'] for w in words)
                        sure = '' if unsure else reply['text']
                        words = []
                    else:
                        reply['text'] = sure = confident_text(recognizer.FinalResult(), min_confidence)
                    if hint_recognizer is not None:
                        alternative = hint_text(hint_results + [hint_recognizer.FinalResult()])
                        hint_results = []
                        if alternative and alternative != reply['text'] and (
                                not sure or SequenceMatcher(None, sure, alternative).ratio() >= HINT_SIMILARITY):
                            reply['alternative'] = alternative
                    await ws.send(json.dumps(reply, ensure_ascii=False))
                    continue
                language = config.get('language') or LANGUAGES[0]
                if language not in models:
                    await ws.close(4400, 'unsupported language')
                    return
                details, words, hint_results = bool(config.get('details')), [], []
                recognizer, min_confidence = make_recognizer(models[language], config.get('grammar'), details)
                hints = config.get('hints')
                hint_recognizer = make_hint_recognizer(models[language], hints) if isinstance(hints, list) else None
                continue

            if recognizer is None:
                recognizer, min_confidence = make_recognizer(models[language], None)
            # Decoding is CPU-bound; keep the event loop free for other connections.
            if hint_recognizer is not None and await loop.run_in_executor(None, hint_recognizer.AcceptWaveform, message):
                hint_results.append(hint_recognizer.Result())
            if await loop.run_in_executor(None, recognizer.AcceptWaveform, message):
                if details:
                    # Words are sent once, with the final reply, to keep timings in one list.
                    words += result_words(recognizer.Result())
                    continue
                text = confident_text(recognizer.Result(), min_confidence)
                if text:
                    await ws.send(json.dumps({'text': text}, ensure_ascii=False))

    return handler


async def main():
    SetLogLevel(-1)
    models = {}
    for code in LANGUAGES:
        log.info('loading %s model from %s/%s', code, MODELS_DIR, code)
        models[code] = Model(os.path.join(MODELS_DIR, code))
    if not SECRET:
        log.warning('VOICE_SECRET is not set: connections are not authenticated')
    port = int(os.environ.get('VOICE_PORT', '2700'))
    async with serve(handler_for(models), '0.0.0.0', port, max_size=MAX_MESSAGE_BYTES):
        log.info('listening on :%s', port)
        await asyncio.get_running_loop().create_future()


if __name__ == '__main__':
    asyncio.run(main())
