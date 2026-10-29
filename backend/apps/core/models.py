from django.db import models


class Level(models.TextChoices):
    """CEFR proficiency levels, shared by grammar rules and vocabulary."""
    A1 = 'A1', 'A1'
    A2 = 'A2', 'A2'
    B1 = 'B1', 'B1'
    B2 = 'B2', 'B2'
    C1 = 'C1', 'C1'
    C2 = 'C2', 'C2'


class Language(models.Model):
    code = models.CharField(max_length=10, unique=True, help_text="ISO 639-1, e.g. 'en'")
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SiteSettings(models.Model):
    """Settings the site owner changes in «Админка → Настройки»: a single row (pk=1).

    An empty field falls back to the setting of the same name in .env (django.conf.settings),
    so a deploy configured before this page existed keeps working. Read them with
    site_setting('club_time_zone').
    """

    google_oauth_client_id = models.CharField('Google OAuth client ID', max_length=200, blank=True)
    club_time_zone = models.CharField('Часовой пояс клуба', max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return 'Настройки сайта'

    @classmethod
    def load(cls):
        return cls.objects.filter(pk=1).first() or cls(pk=1)


def site_setting(name):
    """A SiteSettings field, or the .env setting NAME when it is empty."""
    from django.conf import settings
    return getattr(SiteSettings.load(), name) or getattr(settings, name.upper(), '')
