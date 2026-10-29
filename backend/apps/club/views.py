import json
import logging

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from . import bot, instagram
from .models import InstagramBot

logger = logging.getLogger(__name__)


@csrf_exempt
def instagram_webhook(request, key):
    """The personal webhook of one teacher's bot; its URL and verify token go into their Meta app."""
    account = get_object_or_404(InstagramBot.objects.select_related('teacher'), webhook_key=key)
    if request.method == 'GET':
        # The check Meta makes when the teacher saves the webhook in their app.
        if (request.GET.get('hub.mode') == 'subscribe'
                and request.GET.get('hub.verify_token') == account.verify_token):
            account.webhook_verified_at = timezone.now()
            account.save(update_fields=['webhook_verified_at'])
            return HttpResponse(request.GET.get('hub.challenge', ''), content_type='text/plain')
        return HttpResponseForbidden()
    if request.method != 'POST':
        return HttpResponse(status=405)
    if not instagram.valid_signature(request.body, request.headers.get('X-Hub-Signature-256'), account.app_secret):
        return HttpResponseForbidden()

    try:
        data = json.loads(request.body)
    except ValueError:
        return HttpResponse(status=400)
    account.last_event_at = timezone.now()
    account.save(update_fields=['last_event_at'])
    if not account.is_active:
        return HttpResponse('ok')
    instagram.keep_fresh(account)
    site_url = request.build_absolute_uri('/')
    for entry in data.get('entry', []):
        if str(entry.get('id')) != account.account_id:
            continue
        for event in entry.get('messaging', []):
            try:
                bot.handle_event(account, event, site_url)
            except Exception:
                # Answering 200 anyway: Meta retries failed deliveries and would repeat the bot's replies.
                logger.exception('Instagram event failed: %s', event)
    return HttpResponse('ok')
