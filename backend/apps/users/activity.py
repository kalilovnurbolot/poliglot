"""Activity log: log_activity() for explicit actions, signals for sign-in/out."""

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import ActivityLog

Action = ActivityLog.Action


def client_ip(request):
    # Behind Caddy/nginx the client is the first address in X-Forwarded-For.
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    ip = forwarded.split(',')[0].strip() or request.META.get('REMOTE_ADDR')
    return ip or None


def log_activity(request, action, target='', user=None, email=''):
    """Record `action` by `user` (default: the signed-in user of `request`)."""
    if user is None and request is not None and request.user.is_authenticated:
        user = request.user
    ActivityLog.objects.create(
        user=user,
        user_email=user.email if user else email,
        action=action,
        target=str(target)[:255],
        ip=client_ip(request) if request is not None else None,
    )


@receiver(user_logged_in)
def _logged_in(sender, request, user, **kwargs):
    # Views set login_method before login() when it is not a password sign-in.
    method = getattr(request, 'login_method', None) if request is not None else None
    log_activity(request, Action.LOGIN_GOOGLE if method == 'google' else Action.LOGIN, user=user)


@receiver(user_logged_out)
def _logged_out(sender, request, user, **kwargs):
    if user is not None:
        log_activity(request, Action.LOGOUT, user=user)


@receiver(user_login_failed)
def _login_failed(sender, credentials, request=None, **kwargs):
    email = credentials.get('email') or credentials.get('username') or ''
    log_activity(request, Action.LOGIN_FAILED, email=email[:254])
