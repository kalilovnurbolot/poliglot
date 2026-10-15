from django.db import migrations

# Decks: key -> (name, description). Names matching existing decks (from earlier
# migrations) reuse them via get_or_create; the rest are new.
DECKS = {
    'jobs_hotel': ('Профессии и отель', 'Профессии и лексика об отеле/аэропорте.'),
    'animals': ('Животные', 'Названия животных.'),
    'food_shopping': ('Еда и покупки', 'Еда, напитки и фразы для магазина/кафе.'),
    'accessories': ('Личные вещи', 'Повседневные предметы и аксессуары.'),
    'places': ('Города и места', 'Места в городе и за городом.'),
    'nature': ('Природа', 'Природные явления и ландшафты.'),
    'appearance': ('Внешность и характер', 'Внешность, голос и черты характера.'),
    'abstract': ('Абстрактные понятия', 'Чувства, идеи и жизненные понятия.'),
}

# (deck_key, text, translation, transcription, part_of_speech, level, example_sentence)
WORDS = [
    # --- Personal items & accessories ---
    ('accessories', 'backpack', 'рюкзак', '[ˈbækpæk]', 'noun', 'A1', 'She packed her backpack for school.'),
    ('accessories', 'wallet', 'кошелёк', '[ˈwɒlɪt]', 'noun', 'A1', 'He left his wallet at home.'),
    ('accessories', 'pillow', 'подушка', '[ˈpɪloʊ]', 'noun', 'A1', 'I sleep with two pillows.'),
    ('accessories', 'blanket', 'одеяло', '[ˈblæŋkɪt]', 'noun', 'A1', 'Cover yourself with a blanket.'),
    ('accessories', 'toothbrush', 'зубная щётка', '[ˈtuːθbrʌʃ]', 'noun', 'A1', 'Buy a new toothbrush.'),
    ('accessories', 'headphones', 'наушники', '[ˈhedfoʊnz]', 'noun', 'A1', 'She listens to music with headphones.'),
    ('accessories', 'candle', 'свеча', '[ˈkændəl]', 'noun', 'A1', 'He lit a candle on the table.'),
    ('accessories', 'clock', 'часы', '[klɒk]', 'noun', 'A1', 'The clock on the wall is fast.'),
    ('accessories', 'scissors', 'ножницы', '[ˈsɪzərz]', 'noun', 'A1', 'Cut the paper with scissors.'),
    ('accessories', 'notebook', 'блокнот', '[ˈnoʊtbʊk]', 'noun', 'A1', 'Write it down in your notebook.'),
    ('accessories', 'ladder', 'лестница', '[ˈlædər]', 'noun', 'A2', 'He climbed the ladder to fix the roof.'),
    ('accessories', 'keychain', 'брелок', '[ˈkiːtʃeɪn]', 'noun', 'A2', 'Her keys are on a red keychain.'),
    ('accessories', 'necklace', 'ожерелье', '[ˈnekləs]', 'noun', 'A2', 'She wore a silver necklace.'),
    ('accessories', 'ring', 'кольцо', '[rɪŋ]', 'noun', 'A1', 'He gave her a diamond ring.'),
    ('accessories', 'comb', 'расчёска', '[koʊm]', 'noun', 'A2', 'Use a comb to fix your hair.'),
    ('accessories', 'flashlight', 'фонарик', '[ˈflæʃlaɪt]', 'noun', 'A2', 'Bring a flashlight, it will be dark.'),
    ('accessories', 'charger', 'зарядное устройство', '[ˈtʃɑːrdʒər]', 'noun', 'A2', 'Have you seen my phone charger?'),
    ('accessories', 'remote control', 'пульт', '[rɪˈmoʊt kənˈtroʊl]', 'phrase', 'A2', 'Pass me the remote control, please.'),
    ('accessories', 'envelope', 'конверт', '[ˈenvəloʊp]', 'noun', 'A2', 'Put the letter in an envelope.'),
    ('accessories', 'passport', 'паспорт', '[ˈpæspɔːrt]', 'noun', 'A1', "Don't forget your passport at the airport."),
    ('accessories', 'ticket', 'билет', '[ˈtɪkɪt]', 'noun', 'A1', 'I bought two tickets for the concert.'),
    ('accessories', 'calendar', 'календарь', '[ˈkælɪndər]', 'noun', 'A2', 'Mark the date on the calendar.'),
    ('accessories', 'map', 'карта', '[mæp]', 'noun', 'A1', 'Look at the map to find the street.'),
    ('accessories', 'alarm clock', 'будильник', '[əˈlɑːrm klɒk]', 'phrase', 'A1', 'My alarm clock rings at seven.'),

    # --- Places in the city & beyond ---
    ('places', 'library', 'библиотека', '[ˈlaɪbreri]', 'noun', 'A1', 'I borrowed a book from the library.'),
    ('places', 'hospital', 'больница', '[ˈhɒspɪtəl]', 'noun', 'A1', 'He was taken to the hospital.'),
    ('places', 'supermarket', 'супермаркет', '[ˈsuːpərmɑːrkɪt]', 'noun', 'A1', "Let's go to the supermarket."),
    ('places', 'park', 'парк', '[pɑːrk]', 'noun', 'A1', 'We walked in the park.'),
    ('places', 'museum', 'музей', '[mjuːˈziːəm]', 'noun', 'A1', 'The museum is open on Sundays.'),
    ('places', 'city', 'город', '[ˈsɪti]', 'noun', 'A1', 'New York is a big city.'),
    ('places', 'mountain', 'гора', '[ˈmaʊntən]', 'noun', 'A1', 'They climbed the mountain.'),
    ('places', 'island', 'остров', '[ˈaɪlənd]', 'noun', 'A2', 'They spent their holiday on an island.'),
    ('places', 'village', 'деревня', '[ˈvɪlɪdʒ]', 'noun', 'A2', 'My grandparents live in a small village.'),
    ('places', 'café', 'кафе', '[kæˈfeɪ]', 'noun', 'A1', "Let's meet at the café."),
    ('places', 'hotel', 'отель', '[hoʊˈtel]', 'noun', 'A1', 'We stayed at a nice hotel.'),
    ('places', 'pharmacy', 'аптека', '[ˈfɑːrməsi]', 'noun', 'A2', 'Buy some medicine at the pharmacy.'),
    ('places', 'cinema', 'кинотеатр', '[ˈsɪnəmə]', 'noun', 'A1', "Let's go to the cinema tonight."),
    ('places', 'stadium', 'стадион', '[ˈsteɪdiəm]', 'noun', 'A2', 'The match is at the stadium.'),
    ('places', 'railway station', 'железнодорожный вокзал', '[ˈreɪlweɪ ˈsteɪʃən]', 'phrase', 'A2', 'Meet me at the railway station.'),
    ('places', 'police station', 'полицейский участок', '[pəˈliːs ˈsteɪʃən]', 'phrase', 'A2', 'Report it at the police station.'),
    ('places', 'shopping mall', 'торговый центр', '[ˈʃɒpɪŋ mɔːl]', 'phrase', 'A2', 'We bought clothes at the shopping mall.'),
    ('places', 'playground', 'детская площадка', '[ˈpleɪɡraʊnd]', 'noun', 'A2', 'The children are playing at the playground.'),
    ('places', 'university', 'университет', '[ˌjuːnɪˈvɜːrsəti]', 'noun', 'A2', 'She studies at the university.'),
    ('places', 'gym', 'спортзал', '[dʒɪm]', 'noun', 'A1', 'He goes to the gym every morning.'),
    ('places', 'swimming pool', 'бассейн', '[ˈswɪmɪŋ puːl]', 'phrase', 'A2', 'The hotel has a swimming pool.'),
    ('places', 'bookstore', 'книжный магазин', '[ˈbʊkstɔːr]', 'noun', 'A2', 'I bought this novel at a bookstore.'),
    ('places', 'bank', 'банк', '[bæŋk]', 'noun', 'A1', 'I need to go to the bank.'),
    ('places', 'theater', 'театр', '[ˈθiːətər]', 'noun', 'A2', 'We watched a play at the theater.'),
    ('places', 'countryside', 'сельская местность', '[ˈkʌntrisaɪd]', 'noun', 'A2', 'They live in the countryside.'),

    # --- People & professions ---
    ('jobs_hotel', 'teacher', 'учитель', '[ˈtiːtʃər]', 'noun', 'A1', 'The teacher explained the lesson.'),
    ('jobs_hotel', 'doctor', 'врач', '[ˈdɒktər]', 'noun', 'A1', 'The doctor examined the patient.'),
    ('jobs_hotel', 'photographer', 'фотограф', '[fəˈtɒɡrəfər]', 'noun', 'A2', 'The photographer took great pictures.'),
    ('jobs_hotel', 'tourist', 'турист', '[ˈtʊrɪst]', 'noun', 'A1', 'Tourists visit the old castle every day.'),
    ('jobs_hotel', 'neighbour', 'сосед', '[ˈneɪbər]', 'noun', 'A2', 'My neighbour is very friendly.'),
    ('jobs_hotel', 'athlete', 'спортсмен', '[ˈæθliːt]', 'noun', 'A2', 'The athlete trains every day.'),
    ('jobs_hotel', 'artist', 'художник', '[ˈɑːrtɪst]', 'noun', 'A1', 'The artist painted a beautiful picture.'),
    ('jobs_hotel', 'singer', 'певец', '[ˈsɪŋər]', 'noun', 'A1', 'She is a famous singer.'),
    ('jobs_hotel', 'driver', 'водитель', '[ˈdraɪvər]', 'noun', 'A1', 'The driver stopped at the light.'),

    # --- Animals ---
    ('animals', 'penguin', 'пингвин', '[ˈpeŋɡwɪn]', 'noun', 'A1', "The penguin can't fly."),

    # --- Food ---
    ('food_shopping', 'pizza', 'пицца', '[ˈpiːtsə]', 'noun', 'A1', "Let's order a pizza tonight."),
    ('food_shopping', 'hamburger', 'гамбургер', '[ˈhæmbɜːrɡər]', 'noun', 'A1', 'He ate a hamburger for lunch.'),
    ('food_shopping', 'chocolate', 'шоколад', '[ˈtʃɒklət]', 'noun', 'A1', 'She loves dark chocolate.'),
    ('food_shopping', 'soup', 'суп', '[suːp]', 'noun', 'A1', 'Mom made vegetable soup.'),
    ('food_shopping', 'sandwich', 'бутерброд', '[ˈsænwɪdʒ]', 'noun', 'A1', 'I made a sandwich for breakfast.'),
    ('food_shopping', 'ice cream', 'мороженое', '[aɪs kriːm]', 'phrase', 'A1', 'The children love ice cream.'),
    ('food_shopping', 'cake', 'торт', '[keɪk]', 'noun', 'A1', 'We baked a cake for her birthday.'),

    # --- Nature ---
    ('nature', 'forest', 'лес', '[ˈfɒrɪst]', 'noun', 'A1', 'We walked through the forest.'),
    ('nature', 'waterfall', 'водопад', '[ˈwɔːtərfɔːl]', 'noun', 'A2', 'The waterfall was beautiful.'),
    ('nature', 'river', 'река', '[ˈrɪvər]', 'noun', 'A1', 'The river flows through the city.'),
    ('nature', 'lake', 'озеро', '[leɪk]', 'noun', 'A1', 'We swam in the lake.'),
    ('nature', 'desert', 'пустыня', '[ˈdezərt]', 'noun', 'A2', 'It rarely rains in the desert.'),
    ('nature', 'cave', 'пещера', '[keɪv]', 'noun', 'A2', 'They explored a dark cave.'),
    ('nature', 'volcano', 'вулкан', '[vɒlˈkeɪnoʊ]', 'noun', 'A2', 'The volcano erupted last year.'),
    ('nature', 'rainbow', 'радуга', '[ˈreɪnboʊ]', 'noun', 'A1', 'We saw a rainbow after the rain.'),
    ('nature', 'sunset', 'закат', '[ˈsʌnset]', 'noun', 'A1', 'We watched the sunset on the beach.'),
    ('nature', 'sunrise', 'рассвет', '[ˈsʌnraɪz]', 'noun', 'A1', 'The sunrise was amazing.'),
    ('nature', 'cloud', 'облако', '[klaʊd]', 'noun', 'A1', 'There is a cloud in the sky.'),
    ('nature', 'storm', 'буря', '[stɔːrm]', 'noun', 'A2', 'A storm is coming tonight.'),
    ('nature', 'snowflake', 'снежинка', '[ˈsnoʊfleɪk]', 'noun', 'A2', 'Every snowflake is different.'),
    ('nature', 'wave', 'волна', '[weɪv]', 'noun', 'A2', 'The waves were very big today.'),

    # --- Appearance & character ---
    ('appearance', 'hairstyle', 'причёска', '[ˈherstaɪl]', 'noun', 'B1', 'She has a new hairstyle.'),
    ('appearance', 'uniform', 'форма', '[ˈjuːnɪfɔːrm]', 'noun', 'A2', 'Students wear a school uniform.'),
    ('appearance', 'tattoo', 'татуировка', '[tæˈtuː]', 'noun', 'A2', 'He has a tattoo on his arm.'),
    ('appearance', 'smile', 'улыбка', '[smaɪl]', 'noun', 'A1', 'She has a beautiful smile.'),
    ('appearance', 'voice', 'голос', '[vɔɪs]', 'noun', 'A1', 'I recognized his voice.'),
    ('appearance', 'accent', 'акцент', '[ˈæksent]', 'noun', 'B1', 'She speaks English with a French accent.'),
    ('appearance', 'personality', 'личность, характер', '[ˌpɜːrsəˈnæləti]', 'noun', 'B1', 'He has a great personality.'),

    # --- Abstract & life concepts ---
    ('abstract', 'freedom', 'свобода', '[ˈfriːdəm]', 'noun', 'B1', 'Freedom is very important to her.'),
    ('abstract', 'friendship', 'дружба', '[ˈfrendʃɪp]', 'noun', 'A2', 'Their friendship lasted many years.'),
    ('abstract', 'success', 'успех', '[səkˈses]', 'noun', 'A2', 'Hard work leads to success.'),
    ('abstract', 'happiness', 'счастье', '[ˈhæpinəs]', 'noun', 'A2', "Money can't buy happiness."),
    ('abstract', 'childhood', 'детство', '[ˈtʃaɪldhʊd]', 'noun', 'A2', 'She had a happy childhood.'),
    ('abstract', 'education', 'образование', '[ˌedʒʊˈkeɪʃən]', 'noun', 'A2', 'Education is important for the future.'),
    ('abstract', 'travel', 'путешествия', '[ˈtrævəl]', 'noun', 'A1', 'Travel broadens the mind.'),
    ('abstract', 'technology', 'технологии', '[tekˈnɒlədʒi]', 'noun', 'A2', 'Technology changes very fast.'),
    ('abstract', 'love', 'любовь', '[lʌv]', 'noun', 'A1', 'Love is a strong feeling.'),
    ('abstract', 'responsibility', 'ответственность', '[rɪˌspɒnsəˈbɪləti]', 'noun', 'B1', 'Taking care of a pet is a big responsibility.'),
    ('abstract', 'knowledge', 'знания', '[ˈnɒlɪdʒ]', 'noun', 'B1', 'She has a lot of knowledge about history.'),
    ('abstract', 'experience', 'опыт', '[ɪkˈspɪəriəns]', 'noun', 'B1', 'He has a lot of work experience.'),
    ('abstract', 'opportunity', 'возможность', '[ˌɒpərˈtuːnəti]', 'noun', 'B1', 'This job is a great opportunity.'),
    ('abstract', 'mistake', 'ошибка', '[mɪˈsteɪk]', 'noun', 'A2', 'Everyone makes mistakes sometimes.'),
    ('abstract', 'secret', 'секрет', '[ˈsiːkrət]', 'noun', 'A2', 'Can you keep a secret?'),
    ('abstract', 'advice', 'совет', '[ədˈvaɪs]', 'noun', 'A2', 'Can you give me some advice?'),
    ('abstract', 'problem', 'проблема', '[ˈprɒbləm]', 'noun', 'A1', 'We have a small problem.'),
    ('abstract', 'decision', 'решение', '[dɪˈsɪʒən]', 'noun', 'B1', 'It was a difficult decision.'),
    ('abstract', 'goal', 'цель', '[ɡoʊl]', 'noun', 'A2', 'Her goal is to learn English.'),
    ('abstract', 'adventure', 'приключение', '[ədˈventʃər]', 'noun', 'A2', 'Their trip was a real adventure.'),
    ('abstract', 'challenge', 'вызов, трудность', '[ˈtʃælɪndʒ]', 'noun', 'B1', 'Learning a new language is a challenge.'),
    ('abstract', 'relationship', 'отношения', '[rɪˈleɪʃənʃɪp]', 'noun', 'B1', 'They have a good relationship.'),
    ('abstract', 'tradition', 'традиция', '[trəˈdɪʃən]', 'noun', 'B1', 'This is an old family tradition.'),
    ('abstract', 'culture', 'культура', '[ˈkʌltʃər]', 'noun', 'B1', 'I love learning about other cultures.'),
    ('abstract', 'future', 'будущее', '[ˈfjuːtʃər]', 'noun', 'A2', 'Nobody knows the future.'),
    ('abstract', 'career', 'карьера', '[kəˈrɪr]', 'noun', 'B1', 'She has a successful career.'),
    ('abstract', 'lifestyle', 'образ жизни', '[ˈlaɪfstaɪl]', 'noun', 'B1', 'He has a healthy lifestyle.'),
    ('abstract', 'habit', 'привычка', '[ˈhæbɪt]', 'noun', 'A2', 'Smoking is a bad habit.'),
    ('abstract', 'dream', 'мечта', '[driːm]', 'noun', 'A2', 'Her dream is to travel the world.'),
    ('abstract', 'memory', 'воспоминание', '[ˈmeməri]', 'noun', 'A2', 'This photo brings back good memories.'),
    ('abstract', 'courage', 'смелость', '[ˈkɜːrɪdʒ]', 'noun', 'B1', 'It took courage to speak up.'),
    ('abstract', 'fear', 'страх', '[fɪr]', 'noun', 'A2', 'He has a fear of heights.'),
    ('abstract', 'trust', 'доверие', '[trʌst]', 'noun', 'B1', 'Trust is important in a friendship.'),
    ('abstract', 'luck', 'удача', '[lʌk]', 'noun', 'A2', 'Good luck on your exam!'),
]


def seed_words(apps, schema_editor):
    Language = apps.get_model('core', 'Language')
    Deck = apps.get_model('vocabulary', 'Deck')
    Word = apps.get_model('vocabulary', 'Word')

    english = Language.objects.get(code='en')

    decks = {}
    for key, (name, description) in DECKS.items():
        deck, _ = Deck.objects.get_or_create(
            language=english, owner=None, name=name, defaults={'description': description},
        )
        decks[key] = deck

    for deck_key, text, translation, transcription, part_of_speech, level, example in WORDS:
        word, _ = Word.objects.get_or_create(
            language=english,
            owner=None,
            text=text,
            defaults={
                'translation': translation,
                'transcription': transcription,
                'part_of_speech': part_of_speech,
                'level': level,
                'example_sentence': example,
            },
        )
        word.decks.add(decks[deck_key])


# Deck names that are brand-new in this migration (safe to delete on reverse).
# The rest (Профессии и отель, Животные, Еда и покупки) predate this migration
# and must not be removed on reverse — only unlinked.
NEW_DECK_KEYS = {'accessories', 'places', 'nature', 'appearance', 'abstract'}


def remove_words(apps, schema_editor):
    Deck = apps.get_model('vocabulary', 'Deck')
    Word = apps.get_model('vocabulary', 'Word')

    all_texts = [w[1] for w in WORDS]
    Word.objects.filter(language__code='en', owner__isnull=True, text__in=all_texts).delete()

    new_deck_names = [DECKS[k][0] for k in NEW_DECK_KEYS]
    Deck.objects.filter(owner__isnull=True, language__code='en', name__in=new_deck_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('vocabulary', '0008_seed_textbook_units_vocabulary'),
    ]

    operations = [
        migrations.RunPython(seed_words, remove_words),
    ]
