from django.core.management.base import BaseCommand

from apps.club import instagram
from apps.club.models import InstagramBot


class Command(BaseCommand):
    help = 'Refresh access tokens of connected Instagram bots before they expire (run daily).'

    def handle(self, *args, **options):
        for bot in InstagramBot.objects.exclude(access_token=''):
            instagram.keep_fresh(bot)
