"""Grammar check of a player's answer through the `grammar` service (LanguageTool).

Recognized speech has no capitals or punctuation, so only real grammar mistakes count
(wrong verb form, missing "to", ...), not casing, punctuation or typography.
"""

import json
import logging
import re
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings

log = logging.getLogger(__name__)

LANGUAGE_CODES = {'en': 'en-US', 'de': 'de-DE'}
CATEGORIES = {'GRAMMAR', 'COLLOCATIONS', 'CONFUSED_WORDS', 'NONSTANDARD_PHRASES'}
# Answers take well under a second, but the first check of a language after the service
# starts loads that language (about 4 s for German).
TIMEOUT_SECONDS = 10


def sentence_case(text, language):
    """Recognized speech is all lowercase; grammar rules need "I" and a capital start
    ("can i has" is only caught as "Can I has"). Lengths stay the same, so offsets hold."""
    if language == 'en':
        text = re.sub(r"\bi\b", 'I', text)
    return text[:1].upper() + text[1:]


def check_grammar(text, language):
    """{"errors": [{"wrong", "fix", "message"}], "corrected": text with the fixes applied},
    or None when the service is off or did not answer (the answer is then not judged)."""
    if not settings.GRAMMAR_SERVICE_URL or language not in LANGUAGE_CODES:
        return None
    text = sentence_case(text, language)
    body = urlencode({'text': text, 'language': LANGUAGE_CODES[language]}).encode()
    try:
        with urlopen(f'{settings.GRAMMAR_SERVICE_URL.rstrip("/")}/v2/check', body, timeout=TIMEOUT_SECONDS) as res:
            matches = json.load(res)['matches']
    except (OSError, URLError, ValueError, KeyError) as e:
        log.warning('grammar service unavailable: %s', e)
        return None

    errors, corrected = [], text
    # Fixes are applied from the end so earlier offsets stay valid.
    for m in sorted(matches, key=lambda m: m['offset'], reverse=True):
        if m['rule']['category']['id'] not in CATEGORIES:
            continue
        start, end = m['offset'], m['offset'] + m['length']
        fix = m['replacements'][0]['value'] if m['replacements'] else ''
        errors.append({'wrong': text[start:end], 'fix': fix, 'message': m['message']})
        if fix:
            corrected = corrected[:start] + fix + corrected[end:]
    errors.reverse()
    return {'errors': errors, 'corrected': corrected}
