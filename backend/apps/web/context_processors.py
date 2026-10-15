from django.conf import settings

from apps.core.models import Language

DEFAULT_LANGUAGE = 'en'
SESSION_KEY = 'language'

NAV_LINKS = [
    ('/learn/', 'Учить слова'),
    ('/quiz/', 'Квиз'),
    ('/grammar/', 'Грамматика'),
    ('/words/', 'Мои слова'),
]


def current_language(request):
    """Code of the language being studied, chosen in the navbar and kept in the session."""
    return request.session.get(SESSION_KEY, DEFAULT_LANGUAGE)


def site(request):
    return {
        'languages': Language.objects.all(),
        'language': current_language(request),
        'nav_links': NAV_LINKS,
        'google_client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
    }
