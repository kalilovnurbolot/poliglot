from django.conf import settings

from apps.core.models import Language

from .appearance import appearance_context

DEFAULT_LANGUAGE = 'en'
SESSION_KEY = 'language'

NAV_LINKS = [
    ('/learn/', 'Учить слова'),
    ('/quiz/', 'Квиз'),
    ('/missions/', 'Миссии'),
    ('/grammar/', 'Грамматика'),
    ('/words/', 'Мои слова'),
]


# Ready-made accent colors in the theme panel (navbar); "" is the default indigo.
# Any other color can be picked there too, theme.js builds the palette from it.
THEME_ACCENTS = [
    ('Индиго', '', '#4f46e5'),
    ('Розовый', '#ec4899', '#ec4899'),
    ('Фиолетовый', '#8b5cf6', '#8b5cf6'),
    ('Небесный', '#0ea5e9', '#0ea5e9'),
    ('Изумрудный', '#10b981', '#10b981'),
    ('Оранжевый', '#f97316', '#f97316'),
    ('Красный', '#ef4444', '#ef4444'),
]


def current_language(request):
    """Code of the language being studied, chosen in the navbar and kept in the session."""
    return request.session.get(SESSION_KEY, DEFAULT_LANGUAGE)


def site(request):
    return {
        'languages': Language.objects.all(),
        'language': current_language(request),
        'nav_links': NAV_LINKS,
        'theme_accents': THEME_ACCENTS,
        'appearance': appearance_context(request.user) if request.user.is_authenticated else None,
        'google_client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
    }
