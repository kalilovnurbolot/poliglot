from apps.core.models import Language, site_setting

from .appearance import appearance_context

DEFAULT_LANGUAGE = 'en'
SESSION_KEY = 'language'

# (href, label, icon, short label for the phone tab bar or None if it lives under «Ещё»)
NAV_LINKS = [
    ('/learn/', 'Учить слова', 'cards', 'Учить'),
    ('/quiz/', 'Квиз', 'target', 'Квиз'),
    ('/missions/', 'Миссии', 'flag', 'Миссии'),
    ('/grammar/', 'Грамматика', 'book', 'Правила'),
    ('/words/', 'Мои слова', 'pencil', None),
    ('/verbs/', 'Глаголы', 'repeat', None),
    ('/dictionary/', 'Словарь', 'list', None),
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


def current_section(path):
    """href of the nav section the page belongs to, e.g. '/learn/' for '/learn/session/'."""
    for href, *_ in NAV_LINKS:
        if path.startswith(href):
            return href
    for href in ('/teach/', '/manage/'):
        if path.startswith(href):
            return href
    return None


def site(request):
    section = current_section(request.path)
    return {
        'languages': Language.objects.all(),
        'language': current_language(request),
        'nav_links': NAV_LINKS,
        'nav_section': section,
        # The phone tab bar highlights «Ещё» for sections that live in its sheet.
        'nav_more_active': section is not None and not any(
            href == section and tab for href, _, _, tab in NAV_LINKS
        ),
        'theme_accents': THEME_ACCENTS,
        'appearance': appearance_context(request.user) if request.user.is_authenticated else None,
        'google_client_id': site_setting('google_oauth_client_id'),
    }
