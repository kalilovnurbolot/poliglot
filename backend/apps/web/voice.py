import hashlib
import hmac
import time

from django.conf import settings


def voice_token(user):
    """Short-lived token the voice service checks with the shared VOICE_SECRET
    (see voice/server.py), so only signed-in users of this site can use it."""
    payload = f'{user.pk}:{int(time.time())}'
    signature = hmac.new(settings.VOICE_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f'{payload}:{signature}'


def voice_config(user):
    if not settings.VOICE_URL:
        return None
    return {'url': settings.VOICE_URL, 'token': voice_token(user)}
