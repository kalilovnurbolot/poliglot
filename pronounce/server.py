"""Pronunciation service: which sounds of each word a player got right.

A speech model trained to write down sounds, not words (wav2vec2 on espeak phones),
hears what was actually pronounced; espeak-ng gives how the recognized words should
sound; phones.py compares the two. Its only client is Django (apps/missions/pronunciation.py),
inside the Docker network.

  POST /score?language=en&text=can+i+have+bread   body: mono 16 kHz signed 16-bit PCM
    -> {"score": 0..1, "words": [{"word", "expected", "heard", "score", "subs"}]}
  GET  /health -> {"ok": true}
"""

import json
import logging
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import numpy as np
import torch
from phonemizer.backend import EspeakBackend
from phonemizer.separator import Separator
from transformers import AutoModelForCTC, AutoProcessor

from phones import align, phones

MODEL = os.environ.get('PRONOUNCE_MODEL', 'facebook/wav2vec2-lv-60-espeak-cv-ft')
SAMPLE_RATE = 16000
MAX_SECONDS = 10
MAX_TEXT_LENGTH = 300
ESPEAK_VOICES = {'en': 'en-us', 'de': 'de'}
# phones() splits on spaces; without a phone separator espeak returns whole words.
PHONE_SEPARATOR = Separator(phone=' ', word='')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('pronounce')

torch.set_num_threads(int(os.environ.get('PRONOUNCE_THREADS', '2')))
log.info('loading %s', MODEL)
processor = AutoProcessor.from_pretrained(MODEL)
model = AutoModelForCTC.from_pretrained(MODEL).eval()
espeak = {code: EspeakBackend(voice) for code, voice in ESPEAK_VOICES.items()}
model_lock = threading.Lock()


def heard_phones(pcm):
    audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    inputs = processor(audio, sampling_rate=SAMPLE_RATE, return_tensors='pt').input_values
    with model_lock, torch.no_grad():
        ids = torch.argmax(model(inputs).logits, dim=-1)[0]
    return phones(processor.decode(ids))


def score(pcm, text, language):
    words = re.findall(r"[\w']+", text.lower())
    expected = [phones(p) for p in espeak[language].phonemize(words, separator=PHONE_SEPARATOR, strip=True)] if words else []
    result = align(list(zip(words, expected)), heard_phones(pcm))
    total = sum(len(p) for p in expected)
    overall = sum(w['score'] * len(p) for w, p in zip(result, expected)) / total if total else 0
    return {'score': round(overall, 3), 'words': result}


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/health':
            return self.reply(200, {'ok': True})
        self.reply(404, {'detail': 'not found'})

    def do_POST(self):
        url = urlparse(self.path)
        if url.path != '/score':
            return self.reply(404, {'detail': 'not found'})
        query = parse_qs(url.query)
        language = query.get('language', [''])[0]
        text = query.get('text', [''])[0]
        length = int(self.headers.get('Content-Length') or 0)
        if language not in espeak or len(text) > MAX_TEXT_LENGTH:
            return self.reply(400, {'detail': 'bad language or text'})
        if not 0 < length <= SAMPLE_RATE * 2 * MAX_SECONDS or length % 2:
            return self.reply(400, {'detail': 'bad audio'})
        self.reply(200, score(self.rfile.read(length), text, language))

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    port = int(os.environ.get('PRONOUNCE_PORT', '8030'))
    log.info('listening on :%s', port)
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()
