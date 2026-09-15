from django.db import migrations

WORDS = [
    ('hallo', 'привет', '[haˈloː]', 'other', 'Hallo, wie geht es dir?'),
    ('auf Wiedersehen', 'до свидания', '[ˌaʊfˈviːdɐˌzeːən]', 'other', 'Auf Wiedersehen, bis morgen!'),
    ('bitte', 'пожалуйста', '[ˈbɪtə]', 'other', 'Bitte, mach die Tür zu.'),
    ('danke', 'спасибо', '[ˈdaŋkə]', 'other', 'Danke für deine Hilfe.'),
    ('das Wasser', 'вода', '[das ˈvasɐ]', 'noun', 'Kann ich etwas Wasser haben?'),
    ('das Essen', 'еда', '[das ˈɛsn̩]', 'noun', 'Das Essen hier ist lecker.'),
    ('das Haus', 'дом', '[das haʊs]', 'noun', 'Wir wohnen in einem kleinen Haus.'),
    ('der Freund', 'друг', '[deːɐ̯ frɔɪnt]', 'noun', 'Er ist mein bester Freund.'),
    ('das Buch', 'книга', '[das buːx]', 'noun', 'Ich lese ein neues Buch.'),
    ('die Zeit', 'время', '[diː tsaɪt]', 'noun', 'Wie viel Zeit haben wir?'),
    ('gut', 'хороший', '[ɡuːt]', 'adjective', 'Das ist eine gute Idee.'),
    ('groß', 'большой', '[ɡʁoːs]', 'adjective', 'Sie haben ein großes Auto gekauft.'),
    ('glücklich', 'счастливый', '[ˈɡlʏklɪç]', 'adjective', 'Sie sieht heute glücklich aus.'),
    ('gehen', 'идти / ехать', '[ˈɡeːən]', 'verb', 'Ich gehe jeden Tag zur Schule.'),
    ('essen', 'есть (кушать)', '[ˈɛsn̩]', 'verb', 'Wir essen um 19 Uhr zu Abend.'),
    ('sprechen', 'говорить', '[ˈʃprɛçn̩]', 'verb', 'Sprichst du Deutsch?'),
    ('schnell', 'быстро', '[ʃnɛl]', 'adverb', 'Er rannte schnell zum Bus.'),
    ('heute', 'сегодня', '[ˈhɔʏtə]', 'adverb', 'Heute ist ein schöner Tag.'),
]


def seed_words(apps, schema_editor):
    Language = apps.get_model('core', 'Language')
    Deck = apps.get_model('vocabulary', 'Deck')
    Word = apps.get_model('vocabulary', 'Word')

    german = Language.objects.get(code='de')
    deck, _ = Deck.objects.get_or_create(
        language=german,
        owner=None,
        name='Основы',
        defaults={'description': 'Базовые немецкие слова для начинающих.'},
    )

    for text, translation, transcription, part_of_speech, example in WORDS:
        word, _ = Word.objects.get_or_create(
            language=german,
            owner=None,
            text=text,
            defaults={
                'translation': translation,
                'transcription': transcription,
                'part_of_speech': part_of_speech,
                'example_sentence': example,
            },
        )
        word.decks.add(deck)


def remove_words(apps, schema_editor):
    Deck = apps.get_model('vocabulary', 'Deck')
    Word = apps.get_model('vocabulary', 'Word')
    Word.objects.filter(language__code='de', owner__isnull=True, text__in=[w[0] for w in WORDS]).delete()
    Deck.objects.filter(owner__isnull=True, language__code='de', name='Основы').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('vocabulary', '0003_seed_basic_english_words'),
        ('core', '0003_seed_german_language'),
    ]

    operations = [
        migrations.RunPython(seed_words, remove_words),
    ]
