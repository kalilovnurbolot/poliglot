from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from .models import User


class GoogleAuthError(Exception):
    pass


def user_from_google_token(token):
    """Verify a Google Identity Services id_token and return the matching user,
    creating one (without a usable password) on first sign-in."""
    if not settings.GOOGLE_OAUTH_CLIENT_ID:
        raise GoogleAuthError('Google-вход не настроен на сервере.')

    try:
        payload = google_id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID,
        )
    except ValueError:
        raise GoogleAuthError('Недействительный Google id_token.')

    email = payload.get('email')
    if not email:
        raise GoogleAuthError('Google-аккаунт без email.')

    user, created = User.objects.get_or_create(
        email=email,
        defaults={'first_name': payload.get('given_name', '')},
    )
    if created:
        user.set_unusable_password()
        user.save(update_fields=['password'])
    return user
