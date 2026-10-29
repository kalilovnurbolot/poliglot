"""Instagram API with Instagram Login: the few calls the teachers' bots need.

Every teacher has their own Meta app: they paste its app secret and an access token on
/teach/bot/, and the site's personal webhook URL and verify token into the app.
"""

import hashlib
import hmac
import logging
from datetime import timedelta

import requests
from django.utils import timezone

GRAPH_URL = 'https://graph.instagram.com/v23.0'
TIMEOUT = 10
# Instagram limits: 13 quick replies per message, 20 characters per button title.
MAX_QUICK_REPLIES = 13
MAX_BUTTON_TITLE = 20

logger = logging.getLogger(__name__)


class InstagramError(Exception):
    pass


def _request(method, url, **kwargs):
    try:
        response = requests.request(method, url, timeout=TIMEOUT, **kwargs)
        data = response.json()
    except (requests.RequestException, ValueError) as e:
        raise InstagramError(f'Instagram недоступен: {e}') from e
    if response.status_code >= 400 or 'error' in data or 'error_message' in data:
        error = data.get('error')
        message = (error.get('message') if isinstance(error, dict) else error) \
            or data.get('error_message') or f'HTTP {response.status_code}'
        raise InstagramError(message)
    return data


def _call(method, path, token, **kwargs):
    return _request(method, f'{GRAPH_URL}/{path}', headers={'Authorization': f'Bearer {token}'}, **kwargs)


# ---------- Connecting an account ----------

# Tokens generated in the Meta app dashboard live 60 days.
TOKEN_LIFETIME = timedelta(days=60)


def _long_lived(data):
    return data['access_token'], timezone.now() + timedelta(seconds=int(data.get('expires_in', 0)))


def refresh(token):
    """A long-lived token lasts 60 days; refreshing gives another 60 (only after its first day)."""
    return _long_lived(_request('GET', 'https://graph.instagram.com/refresh_access_token', params={
        'grant_type': 'ig_refresh_token', 'access_token': token,
    }))


# Tokens are refreshed once they have less than this left (webhook events, the teacher's
# page and the refresh_instagram_tokens command all check), so active bots never expire.
REFRESH_BEFORE = timedelta(days=30)


def keep_fresh(bot):
    if not bot.access_token or not bot.token_expires_at or bot.token_expires_at - timezone.now() > REFRESH_BEFORE:
        return
    try:
        bot.access_token, bot.token_expires_at = refresh(bot.access_token)
    except InstagramError as e:
        logger.warning('Refreshing the token of %s failed: %s', bot, e)
        return
    bot.save(update_fields=['access_token', 'token_expires_at'])


def account_info(token):
    """{'user_id', 'username'} of the account the token belongs to."""
    return _call('GET', 'me', token, params={'fields': 'user_id,username'})


def subscribe(token):
    """Start delivering the account's Direct messages to the app's webhook."""
    _call('POST', 'me/subscribed_apps', token, params={'subscribed_fields': 'messages,messaging_postbacks'})


# ---------- Talking to clients ----------

def profile(bot, instagram_id):
    """Username of someone who wrote to the bot, or '' when Instagram won't tell."""
    try:
        return _call('GET', instagram_id, bot.access_token, params={'fields': 'username'}).get('username', '')
    except InstagramError:
        return ''


def send(bot, recipient_id, message):
    _call('POST', 'me/messages', bot.access_token, json={'recipient': {'id': recipient_id}, 'message': message})


def send_text(bot, recipient_id, text, buttons=()):
    """`buttons`: (title, payload) pairs shown as quick replies under the message."""
    message = {'text': text}
    if buttons:
        message['quick_replies'] = [
            {'content_type': 'text', 'title': title[:MAX_BUTTON_TITLE], 'payload': payload}
            for title, payload in buttons[:MAX_QUICK_REPLIES]
        ]
    send(bot, recipient_id, message)


def send_image(bot, recipient_id, url):
    send(bot, recipient_id, {'attachment': {'type': 'image', 'payload': {'url': url}}})


def valid_signature(body, header, secret):
    """X-Hub-Signature-256 of a webhook event: HMAC of the raw body with the app secret."""
    if not secret or not header or not header.startswith('sha256='):
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix('sha256='))
