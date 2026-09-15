from django.db import migrations

# (language_code, deck_name, deck_description, word list)
# word: (text, translation, transcription, part_of_speech, example_sentence)
A2_WORDS = {
    'en': (
        'Продолжаем (A2)',
        'Слова уровня A2 — чуть сложнее базовых.',
        [
            ('weather', 'погода', '[ˈweðər]', 'noun', 'The weather is nice today.'),
            ('restaurant', 'ресторан', '[ˈrestrɒnt]', 'noun', 'We had dinner at a restaurant.'),
            ('money', 'деньги', '[ˈmʌni]', 'noun', 'I don\'t have much money with me.'),
            ('job', 'работа', '[dʒɒb]', 'noun', 'She found a new job last month.'),
            ('weekend', 'выходные', '[ˈwiːkend]', 'noun', 'What are your plans for the weekend?'),
            ('tired', 'уставший', '[ˈtaɪəd]', 'adjective', 'I am tired after work.'),
            ('difficult', 'трудный', '[ˈdɪfɪkəlt]', 'adjective', 'This exercise is quite difficult.'),
            ('expensive', 'дорогой', '[ɪkˈspensɪv]', 'adjective', 'That restaurant is too expensive.'),
            ('to buy', 'покупать', '[baɪ]', 'verb', 'I need to buy some milk.'),
            ('to travel', 'путешествовать', '[ˈtrævl]', 'verb', 'They love to travel abroad.'),
            ('to understand', 'понимать', '[ˌʌndəˈstænd]', 'verb', 'Do you understand this word?'),
            ('usually', 'обычно', '[ˈjuːʒuəli]', 'adverb', 'I usually wake up at 7 am.'),
        ],
    ),
    'de': (
        'Продолжаем (A2)',
        'Слова уровня A2 — чуть сложнее базовых.',
        [
            ('das Wetter', 'погода', '[das ˈvɛtɐ]', 'noun', 'Das Wetter ist heute schön.'),
            ('das Restaurant', 'ресторан', '[ʁɛstoˈʁɑ̃ː]', 'noun', 'Wir haben im Restaurant gegessen.'),
            ('das Geld', 'деньги', '[das ɡɛlt]', 'noun', 'Ich habe nicht viel Geld dabei.'),
            ('die Arbeit', 'работа', '[diː ˈaʁbaɪt]', 'noun', 'Sie hat einen neuen Job gefunden.'),
            ('das Wochenende', 'выходные', '[das ˈvɔxn̩ʔɛndə]', 'noun', 'Was sind deine Pläne fürs Wochenende?'),
            ('müde', 'уставший', '[ˈmyːdə]', 'adjective', 'Ich bin müde nach der Arbeit.'),
            ('schwierig', 'трудный', '[ˈʃviːʁɪç]', 'adjective', 'Diese Übung ist ziemlich schwierig.'),
            ('teuer', 'дорогой', '[ˈtɔɪɐ]', 'adjective', 'Dieses Restaurant ist zu teuer.'),
            ('kaufen', 'покупать', '[ˈkaʊfn̩]', 'verb', 'Ich muss Milch kaufen.'),
            ('reisen', 'путешествовать', '[ˈʁaɪzn̩]', 'verb', 'Sie reisen gerne ins Ausland.'),
            ('verstehen', 'понимать', '[fɛɐ̯ˈʃteːən]', 'verb', 'Verstehst du dieses Wort?'),
            ('meistens', 'обычно', '[ˈmaɪstn̩s]', 'adverb', 'Ich stehe meistens um 7 Uhr auf.'),
        ],
    ),
}


def seed_a2_words(apps, schema_editor):
    Language = apps.get_model('core', 'Language')
    Deck = apps.get_model('vocabulary', 'Deck')
    Word = apps.get_model('vocabulary', 'Word')

    for code, (deck_name, deck_description, words) in A2_WORDS.items():
        language = Language.objects.get(code=code)
        deck, _ = Deck.objects.get_or_create(
            language=language,
            owner=None,
            name=deck_name,
            defaults={'description': deck_description},
        )
        for text, translation, transcription, part_of_speech, example in words:
            word, _ = Word.objects.get_or_create(
                language=language,
                owner=None,
                text=text,
                defaults={
                    'translation': translation,
                    'transcription': transcription,
                    'part_of_speech': part_of_speech,
                    'example_sentence': example,
                    'level': 'A2',
                },
            )
            word.decks.add(deck)


def remove_a2_words(apps, schema_editor):
    Deck = apps.get_model('vocabulary', 'Deck')
    Word = apps.get_model('vocabulary', 'Word')
    for code, (deck_name, _, words) in A2_WORDS.items():
        Word.objects.filter(
            language__code=code, owner__isnull=True, text__in=[w[0] for w in words],
        ).delete()
        Deck.objects.filter(owner__isnull=True, language__code=code, name=deck_name).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('vocabulary', '0005_word_level'),
        ('core', '0003_seed_german_language'),
    ]

    operations = [
        migrations.RunPython(seed_a2_words, remove_a2_words),
    ]
