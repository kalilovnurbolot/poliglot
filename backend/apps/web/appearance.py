"""Site appearance kept in the user's account: mode, accent color and tinted background.

The page is rendered with the saved look already applied (base.html), and theme.js
saves every change back through the `appearance` view. Guests keep it in the browser.
"""

import re

from django.urls import reverse

MODES = ('system', 'light', 'dark')
ACCENT_RE = re.compile(r'^#[0-9a-fA-F]{6}$')


def clean_appearance(data):
    """Validated {"mode", "accent", "tint"} from request data; raises ValueError."""
    mode, accent, tint = data.get('mode'), data.get('accent'), data.get('tint')
    if mode not in MODES or not isinstance(tint, bool):
        raise ValueError
    if accent != '' and not (isinstance(accent, str) and ACCENT_RE.match(accent)):
        raise ValueError
    return {'mode': mode, 'accent': accent.lower(), 'tint': tint}


def appearance_context(user):
    """What base.html and theme.js need for a signed-in user."""
    saved = user.appearance or {}
    return {
        'mode': saved.get('mode', 'system'),
        'accent': saved.get('accent', ''),
        'tint': saved.get('tint', False),
        'saved': bool(saved),
        'hint_seen': user.appearance_hint_seen,
        'url': reverse('web:appearance'),
    }
