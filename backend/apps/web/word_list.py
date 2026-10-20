"""Parse a pasted word list ("word — translation" per line) for «Мои слова»."""

import re

MAX_LINES = 500

BULLET = re.compile(r'^\s*(?:[*•·▪◦‣-]|\d+[.)])\s*')
# The first " — ", " – ", " - " (dashes need spaces around them: "to-do" stays one word),
# ":", "=" or a tab separates the word from its translation.
SEPARATOR = re.compile(r'\s+[—–-]\s+|\s*[:=\t]\s*')
# A line without a separator is a heading; these words in it set the part of speech.
HEADINGS = [
    (re.compile(r'verb|глагол', re.I), 'verb'),
    (re.compile(r'adjective|прилагат', re.I), 'adjective'),
    (re.compile(r'adverb|нареч', re.I), 'adverb'),
    (re.compile(r'phrase|expression|фраз|выражен', re.I), 'phrase'),
    (re.compile(r'noun|существ', re.I), 'noun'),
]


def parse_word_list(text, default_part_of_speech):
    """[(word, translation, part_of_speech)] in the order of the text."""
    words = []
    part_of_speech = default_part_of_speech
    for line in text.splitlines()[:MAX_LINES]:
        line = BULLET.sub('', line).strip()
        if not line:
            continue
        parts = SEPARATOR.split(line, maxsplit=1)
        if len(parts) == 1:
            # "adverb" must not match as "verb": check the longer names first.
            matched = [pos for pattern, pos in HEADINGS if pattern.search(line)]
            part_of_speech = 'adverb' if 'adverb' in matched else (matched[0] if matched else default_part_of_speech)
            continue
        word, translation = (p.strip() for p in parts)
        if word and translation:
            words.append((word[:200], translation[:200], part_of_speech))
    return words
