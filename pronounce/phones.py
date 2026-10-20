"""Comparison of the sounds a player made with the dictionary pronunciation of the words.

Both sides are IPA phones: expected ones from espeak-ng, heard ones from the speech model.
They are aligned like an edit distance; every word gets the share of its sounds that
were pronounced right and the list of sounds that were replaced or dropped.
"""

# Spellings of the same sound on the two sides, and symbols the model sometimes emits
# from other languages' alphabets.
SAME = {'ɹ': 'r', 'ɾ': 'r', 'ʁ': 'r', 'ɡ': 'g', 'ɕ': 'ʃ', 'ʂ': 'ʃ', 'ʑ': 'ʒ', 'ɐ̯': 'r', 'ɚ': 'ər', 'ɝ': 'ɜː'}
DROP = set('ˈˌ0123456789|')

# Sounds the model confuses even in native speech: a swap costs half a mistake.
CLOSE = {frozenset(pair) for pair in [
    ('ə', 'ɛ'), ('ə', 'ɐ'), ('ə', 'ʌ'), ('ə', 'ɪ'), ('ɐ', 'a'), ('e', 'ɛ'), ('o', 'ɔ'), ('oː', 'o'),
    ('eː', 'e'), ('ç', 'ʃ'), ('ʊ', 'u'), ('ɑː', 'ɑ'), ('ɔː', 'ɔ'), ('oʊ', 'o'), ('ɛː', 'ɛ'), ('ər', 'ɜː'),
]}


def normalize(phone):
    phone = ''.join(ch for ch in phone if ch not in DROP)
    return SAME.get(phone, phone)


def phones(text):
    """'aɪ θ ɪ ŋ k' -> ['aɪ', 'θ', 'ɪ', 'ŋ', 'k'] in the shared spelling."""
    return [p for p in (normalize(p) for p in text.split()) if p]


def _cost(a, b):
    if a == b:
        return 0
    return 0.5 if frozenset((a, b)) in CLOSE else 1


def align(expected_words, heard):
    """`expected_words`: [(word, [phones])], `heard`: [phones] of the whole phrase.

    Returns [{"word", "expected", "heard", "score", "subs"}] where "subs" are
    [expected sound, heard sound or ""] pairs of the mistakes in the word.
    """
    expected = [(i, p) for i, (_, ps) in enumerate(expected_words) for p in ps]
    n, m = len(expected), len(heard)
    # dist[i][j]: cheapest way to turn the first i expected sounds into the first j heard.
    dist = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dist[i][0] = i
    for j in range(1, m + 1):
        dist[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dist[i][j] = min(
                dist[i - 1][j - 1] + _cost(expected[i - 1][1], heard[j - 1]),
                dist[i - 1][j] + 1,
                dist[i][j - 1] + 1,
            )

    words = [{'word': w, 'expected': ''.join(ps), 'heard': [], 'errors': 0.0, 'subs': []} for w, ps in expected_words]
    i, j = n, m
    while i or j:
        # An extra heard sound belongs to the word being walked through (or the last one).
        word = words[expected[i - 1][0] if i else 0]
        if i and j and dist[i][j] == dist[i - 1][j - 1] + _cost(expected[i - 1][1], heard[j - 1]):
            cost = _cost(expected[i - 1][1], heard[j - 1])
            word['heard'].append(heard[j - 1])
            word['errors'] += cost
            if cost == 1:
                word['subs'].append([expected[i - 1][1], heard[j - 1]])
            i, j = i - 1, j - 1
        elif i and dist[i][j] == dist[i - 1][j] + 1:
            word['errors'] += 1
            word['subs'].append([expected[i - 1][1], ''])
            i -= 1
        else:
            word['heard'].append(heard[j - 1])
            word['errors'] += 1
            j -= 1

    result = []
    for (w, ps), word in zip(expected_words, words):
        result.append({
            'word': w,
            'expected': word['expected'],
            'heard': ''.join(reversed(word['heard'])),
            'score': round(max(0.0, 1 - word['errors'] / len(ps)), 2) if ps else 1.0,
            'subs': list(reversed(word['subs'])),
        })
    return result
