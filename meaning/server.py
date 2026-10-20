"""Sentence meaning service: turns phrases into vectors whose closeness is closeness of
meaning ("what is the total" is close to "how much is it"), in any language.

Its only client is Django (apps/missions/meaning.py), inside the Docker network.

  POST /embed  {"texts": ["...", ...]}  ->  {"vectors": [[...], ...]}  (unit length)
  GET  /health                          ->  {"ok": true}
"""

import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from fastembed import TextEmbedding

MODEL = os.environ.get('MEANING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
CACHE_DIR = os.environ.get('MEANING_CACHE_DIR', '/models')
MAX_TEXTS = 64
MAX_TEXT_LENGTH = 500
MAX_BODY_BYTES = 64 * 1024

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('meaning')

log.info('loading %s', MODEL)
model = TextEmbedding(MODEL, cache_dir=CACHE_DIR)
model_lock = threading.Lock()


def embed(texts):
    with model_lock:
        vectors = list(model.embed(texts))
    result = []
    for v in vectors:
        length = float((v * v).sum()) ** 0.5 or 1.0
        result.append([round(float(x) / length, 5) for x in v])
    return result


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data):
        body = json.dumps(data).encode()
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
        if self.path != '/embed':
            return self.reply(404, {'detail': 'not found'})
        length = int(self.headers.get('Content-Length') or 0)
        if not 0 < length <= MAX_BODY_BYTES:
            return self.reply(400, {'detail': 'bad body'})
        try:
            texts = json.loads(self.rfile.read(length))['texts']
        except (ValueError, KeyError, TypeError):
            return self.reply(400, {'detail': 'bad json'})
        if (not isinstance(texts, list) or not 0 < len(texts) <= MAX_TEXTS
                or not all(isinstance(t, str) and len(t) <= MAX_TEXT_LENGTH for t in texts)):
            return self.reply(400, {'detail': 'bad texts'})
        self.reply(200, {'vectors': embed(texts)})

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    port = int(os.environ.get('MEANING_PORT', '8020'))
    log.info('listening on :%s', port)
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()
