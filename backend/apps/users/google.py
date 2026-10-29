from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from apps.core.models import site_setting

from .models import User


class GoogleAuthError(Exception):
    pass


def user_from_google_token(token):
    """Verify a Google Identity Services id_token and return the matching user,
    creating one (without a usable password) on first sign-in."""
    client_id = site_setting('google_oauth_client_id')
    if not client_id:
        raise GoogleAuthError('Google-вход не настроен на сервере.')

    try:
        payload = google_id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
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
    if not user.is_active:
        raise GoogleAuthError('Аккаунт заблокирован.')
    return user
