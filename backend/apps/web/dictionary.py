"""Group words by first letter for the «Словарь» page."""

import unicodedata

# Sorted by the word itself, not by what goes before it: "to go" under G, "das Haus" under H.
PREFIXES = {
    'en': ('to ',),
    'de': ('der ', 'die ', 'das ', 'sich '),
}
OTHER = '#'


def headword(text, language):
    lowered = text.strip().lower()
    for prefix in PREFIXES.get(language, ()):
        if lowered.startswith(prefix) and len(lowered) > len(prefix):
            return lowered[len(prefix):]
    return lowered


def sort_key(text, language):
    """Accents stripped, so "ähnlich" goes with "a", not after "z"."""
    decomposed = unicodedata.normalize('NFD', headword(text, language))
    return ''.join(c for c in decomposed if not unicodedata.combining(c)).casefold()


def first_letter(key):
    letter = next((c for c in key if c.isalpha()), '')
    return letter.upper() if len(letter.upper()) == 1 else OTHER


def group_by_letter(words, language):
    """[(letter, [word, ...])] in alphabetical order; words without a letter go last under "#".
    The same word with the same translation (a user's copy of a system word) is shown once."""
    seen = set()
    groups = {}
    for word in sorted(words, key=lambda w: (sort_key(w.text, language), w.text.lower())):
        pair = (word.text.strip().lower(), word.translation.strip().lower())
        if pair in seen:
            continue
        seen.add(pair)
        groups.setdefault(first_letter(sort_key(word.text, language)), []).append(word)
    return sorted(groups.items(), key=lambda item: (item[0] == OTHER, item[0]))
