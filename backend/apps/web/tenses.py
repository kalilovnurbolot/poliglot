"""Three tense forms of a verb for the «Времена» game, and a picture (emoji) for it.

English: I eat / I am eating / I will eat. German has no continuous tense, so the
ongoing action is said with "gerade": ich esse / ich esse gerade / ich werde essen.
Verbs that are not used in the continuous ("to know", "wissen") and modals are left out.
"""

import re

# (name, short name for the barrier, when it is used)
TENSES = {
    'en': [('Present Simple', 'Simple', 'обычно, регулярно'), ('Present Continuous', 'Continuous', 'прямо сейчас'),
           ('Future Simple', 'Future', 'в будущем')],
    'de': [('Präsens', 'Präsens', 'обычно, регулярно'), ('Präsens + gerade', 'gerade', 'прямо сейчас'),
           ('Futur I', 'Futur I', 'в будущем')],
}

EN_SKIP = {
    'be', 'can', 'have', 'know', 'want', 'need', 'like', 'love', 'hate', 'believe', 'mean', 'seem',
    'understand', 'remember', 'suppose', 'require', 'prefer', 'belong', 'own', 'hear', 'see', 'include',
    'must', 'may', 'might', 'should', 'could', 'would', 'shall', 'will',
}
# -ing forms the spelling rules below get wrong (stress on the last syllable, "qu").
EN_ING = {
    'begin': 'beginning', 'forget': 'forgetting', 'prefer': 'preferring', 'occur': 'occurring',
    'admit': 'admitting', 'refer': 'referring', 'permit': 'permitting', 'commit': 'committing',
    'regret': 'regretting', 'control': 'controlling', 'quit': 'quitting', 'travel': 'traveling',
}

DE_SKIP = {
    'sein', 'haben', 'wissen', 'kennen', 'können', 'müssen', 'wollen', 'sollen', 'dürfen', 'mögen',
    'möchten', 'werden', 'verstehen', 'gehören', 'brauchen',
}
# First person singular present that does not follow "stem + e".
DE_ICH = {'tun': 'tue'}
DE_SEPARABLE = ('zurück', 'fern', 'weg', 'los', 'auf', 'aus', 'ein', 'mit', 'nach', 'vor', 'an', 'ab', 'zu')
DE_NOT_SEPARABLE = {'antworten', 'abonnieren'}

# Pictures by the verb itself, English and German side by side.
EMOJI = {
    'go': '🚶', 'gehen': '🚶', 'eat': '🍽️', 'essen': '🍽️', 'speak': '🗣️', 'sprechen': '🗣️',
    'buy': '🛒', 'kaufen': '🛒', 'travel': '✈️', 'reisen': '✈️', 'do': '🛠️', 'machen': '🛠️',
    'say': '💬', 'sagen': '💬', 'get': '📦', 'bekommen': '📦', 'think': '🤔', 'denken': '🤔',
    'take': '🤲', 'nehmen': '🤲', 'come': '🏃', 'kommen': '🏃', 'look': '👀', 'schauen': '👀',
    'use': '🔧', 'benutzen': '🔧', 'find': '🔎', 'finden': '🔎', 'give': '🎁', 'geben': '🎁',
    'tell': '📢', 'erzählen': '📢', 'work': '💼', 'arbeiten': '💼', 'cook': '👨‍🍳', 'kochen': '👨‍🍳',
    'call': '📞', 'anrufen': '📞', 'try': '🎯', 'versuchen': '🎯', 'ask': '🙋', 'fragen': '🙋',
    'feel': '💗', 'fühlen': '💗', 'become': '🦋', 'leave': '🚪', 'verlassen': '🚪', 'put': '📥',
    'legen': '📥', 'keep': '🗄️', 'let': '🤝', 'begin': '🚦', 'beginnen': '🚦', 'help': '🆘',
    'helfen': '🆘', 'turn': '🔄', 'show': '👉', 'zeigen': '👉', 'play': '⚽', 'spielen': '⚽',
    'run': '🏃‍♂️', 'laufen': '🏃‍♂️', 'move': '📦', 'live': '🏠', 'wohnen': '🏠', 'leben': '🏠',
    'hold': '✊', 'halten': '✊', 'bring': '🧺', 'bringen': '🧺', 'happen': '💥', 'write': '✍️',
    'schreiben': '✍️', 'sit': '🪑', 'sitzen': '🪑', 'stand': '🧍', 'stehen': '🧍', 'lose': '😞',
    'verlieren': '😞', 'pay': '💳', 'bezahlen': '💳', 'meet': '🤝', 'treffen': '🤝', 'continue': '⏩',
    'study': '📚', 'lernen': '📚', 'studieren': '📚', 'change': '🔀', 'stop': '🛑', 'create': '🎨',
    'read': '📖', 'lesen': '📖', 'spend': '💸', 'grow': '🌱', 'wachsen': '🌱', 'open': '🔓',
    'öffnen': '🔓', 'win': '🏆', 'gewinnen': '🏆', 'offer': '🫴', 'appear': '✨', 'wait': '⏳',
    'warten': '⏳', 'serve': '🛎️', 'die': '🥀', 'send': '📨', 'schicken': '📨', 'build': '🏗️',
    'bauen': '🏗️', 'drink': '🥤', 'trinken': '🥤', 'stay': '🛋️', 'bleiben': '🛋️', 'fall': '🍂',
    'fallen': '🍂', 'cut': '✂️', 'schneiden': '✂️', 'achieve': '🥇', 'kill': '⚔️', 'hide': '🙈',
    'forget': '🫥', 'vergessen': '🫥', 'answer': '💡', 'antworten': '💡', 'notice': '❗', 'sleep': '😴',
    'schlafen': '😴', 'close': '🔒', 'schließen': '🔒', 'fly': '🕊️', 'fliegen': '🕊️', 'breathe': '🌬️',
    'get dressed': '👕', 'anziehen': '👕', 'earn': '💰', 'verdienen': '💰', 'rest': '🏖️',
    'wash': '🧼', 'waschen': '🧼', 'celebrate': '🎉', 'feiern': '🎉', 'spell': '🔤', 'make': '🛠️',
    'describe': '📝', 'beschreiben': '📝', 'listen': '🎧', 'hören': '🎧', 'swim': '🏊', 'schwimmen': '🏊',
    'sing': '🎤', 'singen': '🎤', 'dance': '💃', 'tanzen': '💃', 'drive': '🚗', 'fahren': '🚗',
    'watch': '📺', 'sehen': '📺', 'clean': '🧹', 'putzen': '🧹', 'draw': '🖍️', 'zeichnen': '🖍️',
    'laugh': '😂', 'lachen': '😂', 'cry': '😢', 'weinen': '😢', 'walk': '🚶', 'climb': '🧗',
    'paint': '🎨', 'malen': '🎨', 'teach': '👩‍🏫', 'unterrichten': '👩‍🏫', 'shop': '🛍️', 'einkaufen': '🛍️',
    'fix': '🔧', 'get up': '⏰', 'aufstehen': '⏰', 'hike': '🥾', 'wandern': '🥾', 'smile': '😊',
    'lächeln': '😊', 'fernsehen': '📺',
}
DEFAULT_EMOJI = '🎬'


def _en_ing(verb):
    if verb in EN_ING:
        return EN_ING[verb]
    if verb.endswith('ie'):
        return verb[:-2] + 'ying'
    if verb.endswith(('ee', 'ye', 'oe')):
        return verb + 'ing'
    if verb.endswith('e') and len(verb) > 2:
        return verb[:-1] + 'ing'
    # One syllable ending in vowel + consonant doubles it: run -> running, stop -> stopping.
    if len(re.findall(r'[aeiou]+', verb)) == 1 and re.search(r'(?:^|[^aeiou])[aeiou][^aeiouwxy]$', verb):
        return verb + verb[-1] + 'ing'
    return verb + 'ing'


def _en_forms(text):
    words = re.sub(r'^to\s+', '', text.strip().lower()).split()
    if not words or words[0] in EN_SKIP or not all(re.fullmatch(r"[a-z']+", w) for w in words):
        return None
    verb, rest = words[0], words[1:]
    return [
        ' '.join(['I', verb, *rest]),
        ' '.join(['I am', _en_ing(verb), *rest]),
        ' '.join(['I will', verb, *rest]),
    ]


def _de_forms(text):
    words = text.strip().lower().split()
    reflexive = words[:1] == ['sich']
    if reflexive:
        words = words[1:]
    if len(words) != 1 or not re.fullmatch(r'[a-zäöüß]+n', words[0]):
        return None
    infinitive = words[0]
    if infinitive in DE_SKIP:
        return None
    particle = next(
        (p for p in DE_SEPARABLE if infinitive.startswith(p) and len(infinitive) - len(p) >= 4
         and infinitive not in DE_NOT_SEPARABLE and not infinitive.endswith('ieren')),
        '',
    )
    stem_verb = infinitive[len(particle):]
    if stem_verb in DE_ICH:
        ich = DE_ICH[stem_verb]
    elif stem_verb.endswith('eln'):
        ich = stem_verb[:-3] + 'le'  # lächeln -> lächle
    elif stem_verb.endswith('en'):
        ich = stem_verb[:-1]  # essen -> esse
    else:
        ich = stem_verb[:-1] + 'e'  # wandern -> wandere
    mich = ['mich'] if reflexive else []
    tail = [particle] if particle else []
    return [
        ' '.join(['ich', ich, *mich, *tail]),
        ' '.join(['ich', ich, *mich, 'gerade', *tail]),
        ' '.join(['ich werde', *mich, infinitive]),
    ]


def tense_forms(text, language):
    """[{tense, short, hint, text}] x 3 for a verb, or None when the game has no forms for it."""
    forms = {'en': _en_forms, 'de': _de_forms}.get(language, lambda _: None)(text)
    if not forms:
        return None
    return [
        {'tense': tense, 'short': short, 'hint': hint, 'text': phrase}
        for (tense, short, hint), phrase in zip(TENSES[language], forms)
    ]


# The barriers of the irregular verbs game: one per form of the table.
FORM_GATES = [
    ('infinitive', 'Infinitive', 'V1', 'начальная форма'),
    ('past', 'Past Simple', 'V2', 'прошедшее время'),
    ('participle', 'Past Participle', 'V3', 'причастие'),
]


def irregular_forms(verb):
    """[{tense, short, hint, text}] for an IrregularVerb: be -> was / were -> been."""
    return [
        {'tense': tense, 'short': short, 'hint': hint, 'text': getattr(verb, field)}
        for field, tense, short, hint in FORM_GATES
    ]


def verb_emoji(text):
    key = re.sub(r'^(to|sich)\s+', '', text.strip().lower())
    return EMOJI.get(key, DEFAULT_EMOJI)
