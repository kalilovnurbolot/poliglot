from django.db import migrations

# Decks: key -> (name, description). Names matching existing decks (from earlier
# migrations) reuse them via get_or_create; the rest are new.
DECKS = {
    'home_kitchen': ('Дом и кухня', 'Немного бытовой лексики.'),
    'adjectives': ('Прилагательные', 'Базовые прилагательные для описания.'),
    'verbs': ('Глаголы', 'Самые частые английские глаголы.'),
    'misc': ('Другие слова', 'Числа, наречия и другие частые слова.'),
    'jobs_hotel': ('Профессии и отель', 'Профессии и лексика об отеле/аэропорте.'),
    'food_shopping': ('Еда и покупки', 'Еда, напитки и фразы для магазина/кафе.'),
    'clothes_colors': ('Одежда и цвета', 'Одежда и цвета.'),
    'phrases': ('Фразы и вопросы', 'Готовые разговорные фразы и вопросы.'),
}

# (deck_key, text, translation, transcription, part_of_speech, level, example_sentence)
WORDS = [
    # --- Household nouns ---
    ('home_kitchen', 'iron', 'утюг', '[ˈaɪərn]', 'noun', 'A1', 'Use the iron to remove wrinkles.'),
    ('home_kitchen', 'knife (knives)', 'нож (ножи)', '[naɪf]', 'noun', 'A1', 'Be careful with that knife.'),
    ('home_kitchen', 'plate', 'тарелка', '[pleɪt]', 'noun', 'A1', 'Put the food on a plate.'),
    ('home_kitchen', 'shelf (shelves)', 'полка (полки)', '[ʃelf]', 'noun', 'A1', 'The books are on the shelf.'),
    ('home_kitchen', 'spoon', 'ложка', '[spuːn]', 'noun', 'A1', 'Eat the soup with a spoon.'),
    ('home_kitchen', 'table', 'стол', '[ˈteɪbəl]', 'noun', 'A1', 'The keys are on the table.'),
    ('home_kitchen', 'towel', 'полотенце', '[ˈtaʊəl]', 'noun', 'A1', 'Dry your hands with a towel.'),
    ('home_kitchen', 'umbrella', 'зонтик', '[ʌmˈbrelə]', 'noun', 'A1', "Take an umbrella, it's raining."),
    ('home_kitchen', 'window', 'окно', '[ˈwɪndoʊ]', 'noun', 'A1', 'Open the window, please.'),

    # --- Home & furniture (Unit 6) ---
    ('home_kitchen', '(tele)phone', 'телефон', '[ˈtelɪfoʊn]', 'noun', 'A1', 'Answer the phone, please.'),
    ('home_kitchen', 'apartment', 'квартира', '[əˈpɑːrtmənt]', 'noun', 'A1', 'They live in a small apartment.'),
    ('home_kitchen', 'balcony', 'балкон', '[ˈbælkəni]', 'noun', 'A1', 'We sat on the balcony.'),
    ('home_kitchen', 'bathroom', 'ванная', '[ˈbæθruːm]', 'noun', 'A1', 'Where is the bathroom?'),
    ('home_kitchen', 'bedroom', 'спальня', '[ˈbedruːm]', 'noun', 'A1', 'My bedroom is upstairs.'),
    ('home_kitchen', 'bottle', 'бутылка', '[ˈbɒtəl]', 'noun', 'A1', 'Fill the bottle with water.'),
    ('home_kitchen', 'cabinet', 'шкафчик', '[ˈkæbɪnɪt]', 'noun', 'A2', 'The plates are in the cabinet.'),
    ('home_kitchen', 'cassette', 'кассета', '[kəˈset]', 'noun', 'A2', 'He listened to an old cassette.'),
    ('home_kitchen', 'CD (compact disc)', 'компакт-диск', '[ˌsiːˈdiː]', 'noun', 'A2', 'I bought a new CD.'),
    ('home_kitchen', 'closet', 'встроенный шкаф, чулан', '[ˈklɒzɪt]', 'noun', 'A2', 'Hang your coat in the closet.'),
    ('home_kitchen', 'coffee table', 'журнальный столик', '[ˈkɒfi ˌteɪbəl]', 'phrase', 'A2', 'The magazine is on the coffee table.'),
    ('home_kitchen', 'desk', 'рабочий стол, парта', '[desk]', 'noun', 'A1', 'She sits at her desk.'),
    ('home_kitchen', 'dining area', 'обеденная зона', '[ˈdaɪnɪŋ ˌeriə]', 'phrase', 'A2', 'We ate in the dining area.'),
    ('home_kitchen', 'dining room', 'столовая (комната)', '[ˈdaɪnɪŋ ruːm]', 'phrase', 'A1', 'Dinner is in the dining room.'),
    ('home_kitchen', 'dishwasher', 'посудомоечная машина', '[ˈdɪʃˌwɒʃər]', 'noun', 'A2', 'Put the plates in the dishwasher.'),
    ('home_kitchen', 'downstairs', 'нижний этаж', '[ˌdaʊnˈsterz]', 'adverb', 'A1', 'The kitchen is downstairs.'),
    ('home_kitchen', 'drawer', 'выдвижной ящик', '[drɔːr]', 'noun', 'A2', 'The spoons are in the drawer.'),
    ('home_kitchen', 'fax machine', 'факсовый аппарат', '[fæks məˈʃiːn]', 'phrase', 'A2', 'Send it by fax machine.'),
    ('home_kitchen', 'floor plan', 'план этажа', '[flɔːr plæn]', 'phrase', 'A2', 'Look at the floor plan.'),
    ('home_kitchen', 'floppy disk', 'дискета', '[ˈflɒpi dɪsk]', 'phrase', 'A2', 'Nobody uses a floppy disk anymore.'),
    ('home_kitchen', 'garage', 'гараж', '[ɡəˈrɑːʒ]', 'noun', 'A1', 'The car is in the garage.'),
    ('home_kitchen', 'hall', 'холл, коридор', '[hɔːl]', 'noun', 'A2', 'Wait for me in the hall.'),
    ('home_kitchen', 'kitchen', 'кухня', '[ˈkɪtʃɪn]', 'noun', 'A1', 'Mom is cooking in the kitchen.'),
    ('home_kitchen', 'lamp', 'лампа', '[læmp]', 'noun', 'A1', 'Turn on the lamp.'),
    ('home_kitchen', 'landing', 'лестничная площадка', '[ˈlændɪŋ]', 'noun', 'A2', 'The door is on the landing.'),
    ('home_kitchen', 'living room', 'гостиная', '[ˈlɪvɪŋ ruːm]', 'phrase', 'A1', 'We watch TV in the living room.'),
    ('home_kitchen', 'magazine', 'журнал', '[ˌmæɡəˈziːn]', 'noun', 'A1', 'She is reading a magazine.'),
    ('home_kitchen', 'mirror', 'зеркало', '[ˈmɪrər]', 'noun', 'A1', 'Look in the mirror.'),
    ('home_kitchen', 'realtor', 'агент по недвижимости', '[ˈriːəltər]', 'noun', 'A2', 'The realtor showed us the house.'),
    ('home_kitchen', 'realty', 'агентство недвижимости', '[ˈriːəlti]', 'noun', 'A2', 'She works at a realty office.'),
    ('home_kitchen', 'refrigerator', 'холодильник', '[rɪˈfrɪdʒəreɪtər]', 'noun', 'A1', 'Put the milk in the refrigerator.'),
    ('home_kitchen', 'rug', 'коврик', '[rʌɡ]', 'noun', 'A2', 'There is a rug on the floor.'),
    ('home_kitchen', 'sink', 'раковина', '[sɪŋk]', 'noun', 'A1', 'Wash your hands in the sink.'),
    ('home_kitchen', 'space', 'место, пространство', '[speɪs]', 'noun', 'A2', "There isn't much space here."),
    ('home_kitchen', 'stove', 'кухонная плита', '[stoʊv]', 'noun', 'A1', 'The soup is on the stove.'),
    ('home_kitchen', 'TV (television)', 'телевизор', '[ˌtiːˈviː]', 'noun', 'A1', 'We watched TV last night.'),
    ('home_kitchen', 'upstairs', 'верхний этаж', '[ˌʌpˈsterz]', 'adverb', 'A1', 'The bedrooms are upstairs.'),
    ('home_kitchen', 'VCR (Video Cassette Recorder)', 'видеомагнитофон', '[ˌviːsiːˈɑːr]', 'phrase', 'A2', 'We still have an old VCR.'),
    ('home_kitchen', 'videocassette', 'видеокассета', '[ˌvɪdioʊkəˈset]', 'noun', 'A2', 'He found an old videocassette.'),
    ('home_kitchen', 'wastepaper basket', 'урна', '[ˈweɪstpeɪpər ˌbæskɪt]', 'phrase', 'A2', 'Throw it in the wastepaper basket.'),
    ('home_kitchen', 'word processor', 'текстовый процессор', '[wɜːrd ˈprɒsesər]', 'phrase', 'A2', 'I wrote the letter on a word processor.'),

    # --- Adjectives & colors ---
    ('adjectives', 'irregular', 'неправильный', '[ɪˈreɡjələr]', 'adjective', 'A2', 'This is an irregular verb.'),
    ('adjectives', 'international', 'международный', '[ˌɪntərˈnæʃənəl]', 'adjective', 'A2', "It's an international company."),
    ('adjectives', 'angry', 'сердитый, злой', '[ˈæŋɡri]', 'adjective', 'A1', 'He was angry about the delay.'),
    ('adjectives', 'closed', 'закрытый', '[kloʊzd]', 'adjective', 'A1', 'The shop is closed today.'),
    ('adjectives', 'cold', 'холодный', '[koʊld]', 'adjective', 'A1', 'The water is very cold.'),
    ('adjectives', 'cool', 'прохладный', '[kuːl]', 'adjective', 'A1', "It's cool in the evening."),
    ('adjectives', 'empty', 'пустой', '[ˈempti]', 'adjective', 'A1', 'The bottle is empty.'),
    ('adjectives', 'full', 'полный', '[fʊl]', 'adjective', 'A1', 'The bus is full.'),
    ('adjectives', 'hot', 'горячий, жаркий', '[hɒt]', 'adjective', 'A1', 'Be careful, the pan is hot.'),
    ('adjectives', 'late', 'поздний, опоздавший', '[leɪt]', 'adjective', 'A1', "Sorry, I'm late."),
    ('adjectives', 'right', 'правильный', '[raɪt]', 'adjective', 'A1', "That's the right answer."),
    ('adjectives', 'regular', 'стандартного размера', '[ˈreɡjələr]', 'adjective', 'A2', "I'd like a regular coffee, please."),
    ('adjectives', 'large', 'большой', '[lɑːrdʒ]', 'adjective', 'A1', 'They live in a large house.'),
    ('adjectives', 'nice', 'хороший, приятный', '[naɪs]', 'adjective', 'A1', 'It is nice to meet you.'),
    ('adjectives', 'sorry', 'сожалеющий, извиняющийся', '[ˈsɒri]', 'adjective', 'A1', "I'm sorry for being late."),
    ('adjectives', 'terrible', 'ужасный', '[ˈterəbəl]', 'adjective', 'A2', 'The weather was terrible.'),
    ('adjectives', 'thick', 'толстый', '[θɪk]', 'adjective', 'A2', 'This book is very thick.'),
    ('adjectives', 'thin', 'тонкий', '[θɪn]', 'adjective', 'A2', 'The ice is too thin.'),
    ('adjectives', 'thirsty', 'испытывающий жажду', '[ˈθɜːrsti]', 'adjective', 'A1', 'I am thirsty, can I have some water?'),
    ('adjectives', 'warm', 'тёплый', '[wɔːrm]', 'adjective', 'A1', "It's warm today."),
    ('adjectives', 'black', 'чёрный', '[blæk]', 'adjective', 'A1', 'She has a black bag.'),
    ('adjectives', 'blue', 'голубой, синий', '[bluː]', 'adjective', 'A1', 'The sky is blue.'),
    ('adjectives', 'brown', 'коричневый', '[braʊn]', 'adjective', 'A1', 'He has brown eyes.'),
    ('adjectives', 'gray', 'серый', '[ɡreɪ]', 'adjective', 'A1', 'The sky is gray today.'),

    # --- Verbs ---
    ('verbs', 'to spell', 'произносить по буквам', '[tuː spel]', 'verb', 'A2', 'Can you spell your name, please?'),
    ('verbs', 'to make', 'делать, составлять', '[tuː meɪk]', 'verb', 'A1', "Let's make dinner together."),
    ('verbs', 'to describe', 'описывать', '[tuː dɪˈskraɪb]', 'verb', 'A2', 'Can you describe the man?'),
    ('verbs', 'to listen', 'слушать', '[tuː ˈlɪsən]', 'verb', 'A1', 'Listen to the music.'),

    # --- Grammar terms, pronouns, prepositions, numbers, misc nouns ---
    ('misc', 'noun', 'существительное', '[naʊn]', 'noun', 'A2', '"Table" is a noun.'),
    ('misc', 'plural', 'множественное число', '[ˈplʊrəl]', 'noun', 'A2', '"Cats" is the plural of "cat".'),
    ('misc', 'singular', 'единственное число', '[ˈsɪŋɡjələr]', 'noun', 'A2', '"Cat" is singular.'),
    ('misc', 'adjective (adj)', 'прилагательное', '[ˈædʒɪktɪv]', 'noun', 'A2', '"Big" is an adjective.'),
    ('misc', 'sentence', 'предложение', '[ˈsentəns]', 'noun', 'A2', 'Write a sentence with this word.'),
    ('misc', 'that', 'тот, та, то', '[ðæt]', 'other', 'A1', 'That is my book.'),
    ('misc', 'these', 'эти', '[ðiːz]', 'other', 'A1', 'These are my keys.'),
    ('misc', 'those', 'те', '[ðoʊz]', 'other', 'A1', 'Those are her shoes.'),
    ('misc', 'her', 'её', '[hɜːr]', 'other', 'A1', 'This is her bag.'),
    ('misc', 'his', 'его', '[hɪz]', 'other', 'A1', 'This is his car.'),
    ('misc', 'its', 'его, её', '[ɪts]', 'other', 'A2', 'The dog wagged its tail.'),
    ('misc', 'my', 'мой, моя, моё, мои', '[maɪ]', 'other', 'A1', 'This is my house.'),
    ('misc', 'our', 'наш, наша, наше, наши', '[ˈaʊər]', 'other', 'A1', 'This is our house.'),
    ('misc', 'their', 'их', '[ðer]', 'other', 'A1', 'This is their car.'),
    ('misc', 'your', 'ваш, твой', '[jɔːr]', 'other', 'A1', 'What is your name?'),
    ('misc', 'but', 'но', '[bʌt]', 'other', 'A1', "I'm tired, but happy."),
    ('misc', 'or', 'или', '[ɔːr]', 'other', 'A1', 'Tea or coffee?'),
    ('misc', 'about', 'о, об, про', '[əˈbaʊt]', 'other', 'A1', 'Tell me about your day.'),
    ('misc', 'any', 'сколько-нибудь', '[ˈeni]', 'other', 'A1', 'Do you have any bread?'),
    ('misc', 'for', 'для, за, на', '[fɔːr]', 'other', 'A1', 'This gift is for you.'),
    ('misc', 'in', 'в', '[ɪn]', 'other', 'A1', 'The keys are in the bag.'),
    ('misc', 'on', 'на', '[ɒn]', 'other', 'A1', 'The book is on the table.'),
    ('misc', 'under', 'под', '[ˈʌndər]', 'other', 'A1', 'The cat is under the table.'),
    ('misc', 'with', 'с', '[wɪð]', 'other', 'A1', 'I live with my parents.'),
    ('misc', 'some', 'несколько, немного', '[sʌm]', 'other', 'A1', 'I need some milk.'),
    ('misc', 'now', 'сейчас', '[naʊ]', 'adverb', 'A1', "I'm busy now."),
    ('misc', 'over here', 'вот здесь', '[ˈoʊvər hɪr]', 'phrase', 'A1', 'Come over here.'),
    ('misc', 'over there', 'вон там', '[ˈoʊvər ðer]', 'phrase', 'A1', 'The shop is over there.'),
    ('misc', 'on the right', 'справа', '[ɒn ðə raɪt]', 'phrase', 'A1', 'The bank is on the right.'),
    ('misc', 'on time', 'вовремя', '[ɒn taɪm]', 'phrase', 'A1', 'The train arrived on time.'),
    ('misc', 'thirteen', 'тринадцать', '[ˌθɜːrˈtiːn]', 'other', 'A1', 'I have thirteen books.'),
    ('misc', 'fourteen', 'четырнадцать', '[ˌfɔːrˈtiːn]', 'other', 'A1', 'She is fourteen years old.'),
    ('misc', 'fifteen', 'пятнадцать', '[ˌfɪfˈtiːn]', 'other', 'A1', 'There are fifteen students.'),
    ('misc', 'sixteen', 'шестнадцать', '[ˌsɪksˈtiːn]', 'other', 'A1', 'He is sixteen.'),
    ('misc', 'seventeen', 'семнадцать', '[ˌsevənˈtiːn]', 'other', 'A1', 'Room seventeen, please.'),
    ('misc', 'eighteen', 'восемнадцать', '[ˌeɪˈtiːn]', 'other', 'A1', 'She turned eighteen.'),
    ('misc', 'nineteen', 'девятнадцать', '[ˌnaɪnˈtiːn]', 'other', 'A1', 'It costs nineteen dollars.'),
    ('misc', 'twenty', 'двадцать', '[ˈtwenti]', 'other', 'A1', 'I have twenty dollars.'),
    ('misc', 'thirty', 'тридцать', '[ˈθɜːrti]', 'other', 'A1', 'She is thirty years old.'),
    ('misc', 'forty', 'сорок', '[ˈfɔːrti]', 'other', 'A1', 'He is forty years old.'),
    ('misc', 'fifty', 'пятьдесят', '[ˈfɪfti]', 'other', 'A1', 'It costs fifty dollars.'),
    ('misc', 'sixty', 'шестьдесят', '[ˈsɪksti]', 'other', 'A1', 'The speed limit is sixty.'),
    ('misc', 'seventy', 'семьдесят', '[ˈsevənti]', 'other', 'A1', 'My grandmother is seventy.'),
    ('misc', 'eighty', 'восемьдесят', '[ˈeɪti]', 'other', 'A1', 'The room number is eighty.'),
    ('misc', 'ninety', 'девяносто', '[ˈnaɪnti]', 'other', 'A1', 'It costs ninety cents.'),
    ('misc', 'mosquito', 'комар', '[məˈskiːtoʊ]', 'noun', 'A1', 'A mosquito bit me.'),
    ('misc', 'radio', 'радио', '[ˈreɪdioʊ]', 'noun', 'A1', 'Turn on the radio.'),
    ('misc', 'taxi', 'такси', '[ˈtæksi]', 'noun', 'A1', "Let's take a taxi."),
    ('misc', 'train', 'поезд', '[treɪn]', 'noun', 'A1', 'The train is late.'),
    ('misc', 'truck', 'грузовик', '[trʌk]', 'noun', 'A1', 'The truck is very big.'),
    ('misc', 'pen', 'ручка', '[pen]', 'noun', 'A1', 'Can I borrow your pen?'),
    ('misc', 'purse', 'кошелёк, сумочка', '[pɜːrs]', 'noun', 'A2', 'She put the money in her purse.'),
    ('misc', 'key', 'ключ', '[kiː]', 'noun', 'A1', 'I lost my key.'),
    ('misc', 'letter', 'буква', '[ˈletər]', 'noun', 'A1', 'The word starts with the letter A.'),
    ('misc', 'word', 'слово', '[wɜːrd]', 'noun', 'A1', 'What does this word mean?'),
    ('misc', 'watch', 'часы (наручные)', '[wɒtʃ]', 'noun', 'A1', 'He is wearing a watch.'),
    ('misc', 'class', 'класс, группа', '[klæs]', 'noun', 'A1', 'Our class has twenty students.'),

    # --- Common phrases & questions ---
    ('phrases', 'Oh, no!', 'О, нет!', '[oʊ noʊ]', 'phrase', 'A1', 'Oh, no! I forgot my keys.'),
    ('phrases', 'What ...?', 'Что?', '[wʌt]', 'phrase', 'A1', 'What is this?'),
    ('phrases', 'What are they/these/those?', 'Что это? (мн.ч.)', '[wʌt ɑːr ðeɪ]', 'phrase', 'A1', 'What are those on the table?'),
    ('phrases', 'What is it/this/that?', 'Что это?', '[wʌt ɪz ɪt]', 'phrase', 'A1', 'What is that noise?'),
    ('phrases', "(My) name's ...", '(Меня) зовут ...', '[maɪ neɪmz]', 'phrase', 'A1', "My name's Anna."),
    ('phrases', '(Our) names are ...', '(Нас) зовут ...', '[aʊər neɪmz ɑːr]', 'phrase', 'A1', 'Our names are Tom and Ben.'),
    ('phrases', 'Good evening!', 'Добрый вечер!', '[ɡʊd ˈiːvnɪŋ]', 'phrase', 'A1', 'Good evening! Please, come in.'),
    ('phrases', "Here's ...", 'Вот ...', '[hɪrz]', 'phrase', 'A1', "Here's your coffee."),
    ('phrases', "I'm sorry.", 'Простите. Мне жаль.', '[aɪm ˈsɒri]', 'phrase', 'A1', "I'm sorry, I didn't mean it."),
    ('phrases', 'Oh, yes!', 'О, да!', '[oʊ jes]', 'phrase', 'A1', 'Oh, yes! I remember now.'),
    ('phrases', "What're (your) jobs?", 'Кем вы работаете?', '[wɒt ɑːr jɔːr dʒɒbz]', 'phrase', 'A2', "What're your jobs?"),
    ('phrases', "What're (your) names?", 'Как (вас) зовут?', '[wɒt ɑːr jɔːr neɪmz]', 'phrase', 'A2', "What're your names?"),
    ('phrases', "What's (your) job?", 'Кем вы работаете?', '[wʌts jɔːr dʒɒb]', 'phrase', 'A1', "What's your job?"),
    ('phrases', "What's (your) name?", 'Как (вас) зовут?', '[wʌts jɔːr neɪm]', 'phrase', 'A1', "What's your name?"),
    ('phrases', "What's the number?", 'Какой номер?', '[wʌts ðə ˈnʌmbər]', 'phrase', 'A1', "What's the number of your room?"),
    ('phrases', "You're welcome.", 'Не за что. Пожалуйста.', '[jʊr ˈwelkəm]', 'phrase', 'A1', 'Thank you! — You are welcome.'),
    ('phrases', 'Brr!', 'Брр!', '[brː]', 'phrase', 'A1', "Brr! It's freezing outside."),
    ('phrases', 'Do the same.', 'Сделайте также.', '[duː ðə seɪm]', 'phrase', 'A2', 'Now do the same with this word.'),
    ('phrases', 'Phew!', 'Фу! Уф!', '[fjuː]', 'phrase', 'A1', 'Phew! That was hard work.'),
    ('phrases', 'Well, ...', 'Ну, ... Итак, ...', '[wel]', 'phrase', 'A2', "Well, let's start."),
    ('phrases', 'Where ...?', 'Где ...?', '[wer]', 'phrase', 'A1', 'Where are you?'),
    ('phrases', 'Where are (the glasses)?', 'Где стаканы?', '[wer ɑːr ðə ˈɡlæsɪz]', 'phrase', 'A1', 'Where are the glasses?'),
    ('phrases', 'Where is (the bathroom)?', 'Где ванная?', '[wer ɪz ðə ˈbæθruːm]', 'phrase', 'A1', 'Where is the bathroom?'),
    ('phrases', 'And (the pepper)?', 'А (перец)?', '[ænd ðə ˈpepər]', 'phrase', 'A2', 'And the pepper? Where is it?'),
    ('phrases', 'Could I have (your phone number), please?', 'Могу я взять ваш телефон, пожалуйста?', '[kʊd aɪ hæv jɔːr foʊn ˈnʌmbər pliːz]', 'phrase', 'A2', 'Could I have your phone number, please?'),
    ('phrases', 'Could you pass (the salt), please?', 'Не могли бы вы передать соль, пожалуйста?', '[kʊd juː pæs ðə sɔːlt pliːz]', 'phrase', 'A2', 'Could you pass the salt, please?'),
    ('phrases', 'Here it is.', 'Вот, пожалуйста.', '[hɪr ɪt ɪz]', 'phrase', 'A1', 'Here it is, your coffee.'),
    ('phrases', 'Here you are.', 'Вот, пожалуйста.', '[hɪr juː ɑːr]', 'phrase', 'A1', 'Here you are, sir.'),
    ('phrases', 'Here you go.', 'Вот, пожалуйста.', '[hɪr juː ɡoʊ]', 'phrase', 'A1', 'Here you go, enjoy your meal.'),
    ('phrases', 'How much are they/these/those?', 'Сколько это стоит?', '[haʊ mʌtʃ ɑːr ðeɪ]', 'phrase', 'A1', 'How much are these apples?'),
    ('phrases', 'How much is it/this/that?', 'Сколько это стоит?', '[haʊ mʌtʃ ɪz ɪt]', 'phrase', 'A1', 'How much is this bag?'),
    ('phrases', 'OK.', 'Ладно. Хорошо.', '[ˌoʊˈkeɪ]', 'phrase', 'A1', "OK, let's go."),
    ('phrases', 'Good.', 'Хорошо.', '[ɡʊd]', 'phrase', 'A1', 'Good. See you tomorrow.'),
    ('phrases', 'Sure.', 'Конечно.', '[ʃʊr]', 'phrase', 'A1', 'Sure, no problem.'),
    ('phrases', "That's OK.", 'Всё в порядке.', '[ðæts ˌoʊˈkeɪ]', 'phrase', 'A1', "Don't worry, that's OK."),
    ('phrases', 'There you are.', 'Вот, пожалуйста.', '[ðer juː ɑːr]', 'phrase', 'A1', 'There you are, madam.'),
    ('phrases', 'There you go.', 'Вот, пожалуйста.', '[ðer juː ɡoʊ]', 'phrase', 'A1', 'There you go, thank you.'),
    ('phrases', 'Very funny.', 'Очень смешно.', '[ˈveri ˈfʌni]', 'phrase', 'A2', "Very funny, but it's true."),
    ('phrases', "What's (your) phone number?", 'Какой (ваш) телефонный номер?', '[wʌts jɔːr foʊn ˈnʌmbər]', 'phrase', 'A1', "What's your phone number?"),

    # --- Jobs & hotel ---
    ('jobs_hotel', 'airport', 'аэропорт', '[ˈerpɔːrt]', 'noun', 'A1', 'The airport is far from here.'),
    ('jobs_hotel', 'bell captain', 'швейцар, носильщик', '[bel ˈkæptɪn]', 'phrase', 'A2', 'The bell captain took our bags.'),
    ('jobs_hotel', 'cashier', 'кассир', '[kæˈʃɪr]', 'noun', 'A1', 'Pay the cashier, please.'),
    ('jobs_hotel', 'cook', 'повар', '[kʊk]', 'noun', 'A1', 'The cook made a delicious meal.'),
    ('jobs_hotel', 'desk clerk', 'портье, администратор', '[desk klɜːrk]', 'phrase', 'A2', 'Ask the desk clerk for a key.'),
    ('jobs_hotel', 'flight attendant', 'бортпроводник, стюардесса', '[flaɪt əˈtendənt]', 'phrase', 'A2', 'The flight attendant brought some water.'),
    ('jobs_hotel', 'hotel manager', 'управляющий гостиницей', '[hoʊˈtel ˈmænɪdʒər]', 'phrase', 'A2', 'The hotel manager greeted the guests.'),
    ('jobs_hotel', 'housekeeper', 'горничная, домработница', '[ˈhaʊsˌkiːpər]', 'noun', 'A2', 'The housekeeper cleaned the room.'),
    ('jobs_hotel', 'mechanic', 'механик', '[məˈkænɪk]', 'noun', 'A1', 'The mechanic fixed my car.'),
    ('jobs_hotel', 'Mr.', 'мистер, господин', '[ˈmɪstər]', 'noun', 'A1', 'Mr. Smith is my teacher.'),
    ('jobs_hotel', 'Mrs.', 'миссис, госпожа', '[ˈmɪsɪz]', 'noun', 'A1', 'Mrs. Brown lives next door.'),
    ('jobs_hotel', 'name', 'имя', '[neɪm]', 'noun', 'A1', 'What is your name?'),
    ('jobs_hotel', 'office', 'офис', '[ˈɒfɪs]', 'noun', 'A1', 'She works in an office.'),
    ('jobs_hotel', 'pilot', 'лётчик, пилот', '[ˈpaɪlət]', 'noun', 'A1', 'The pilot landed the plane safely.'),
    ('jobs_hotel', 'police', 'полиция', '[pəˈliːs]', 'noun', 'A1', 'Call the police!'),
    ('jobs_hotel', 'police officer', 'полицейский', '[pəˈliːs ˈɒfɪsər]', 'phrase', 'A1', 'The police officer helped us.'),
    ('jobs_hotel', 'Portuguese', 'португалец', '[ˌpɔːrtʃʊˈɡiːz]', 'noun', 'A2', 'He is Portuguese.'),
    ('jobs_hotel', 'room', 'комната', '[ruːm]', 'noun', 'A1', 'This is my room.'),
    ('jobs_hotel', 'secretary', 'секретарь', '[ˈsekrəteri]', 'noun', 'A1', 'The secretary answered the phone.'),
    ('jobs_hotel', 'Sir.', 'сэр, господин', '[sɜːr]', 'noun', 'A1', 'Excuse me, Sir.'),
    ('jobs_hotel', 'suitcase', 'чемодан', '[ˈsuːtkeɪs]', 'noun', 'A1', 'Pack your suitcase.'),
    ('jobs_hotel', 'taxi driver', 'таксист', '[ˈtæksi ˈdraɪvər]', 'phrase', 'A1', 'The taxi driver knew the way.'),
    ('jobs_hotel', 'waiter', 'официант', '[ˈweɪtər]', 'noun', 'A1', 'The waiter brought the menu.'),
    ('jobs_hotel', 'waitress', 'официантка', '[ˈweɪtrəs]', 'noun', 'A1', 'The waitress was very friendly.'),

    # --- Food & shopping ---
    ('food_shopping', 'bread', 'хлеб', '[bred]', 'noun', 'A1', 'I bought some bread.'),
    ('food_shopping', 'cent (¢)', 'цент', '[sent]', 'noun', 'A1', 'It costs fifty cents.'),
    ('food_shopping', 'cola', 'кола', '[ˈkoʊlə]', 'noun', 'A1', 'Can I have a cola, please?'),
    ('food_shopping', 'diet cola', 'диетическая кола', '[ˈdaɪət ˈkoʊlə]', 'phrase', 'A2', "I'll have a diet cola."),
    ('food_shopping', 'dollar ($)', 'доллар', '[ˈdɒlər]', 'noun', 'A1', 'It costs ten dollars.'),
    ('food_shopping', 'first name', 'имя', '[fɜːrst neɪm]', 'phrase', 'A1', "What's your first name?"),
    ('food_shopping', 'gallon (= 3.785 liters)', 'галлон', '[ˈɡælən]', 'noun', 'A2', 'Buy a gallon of milk.'),
    ('food_shopping', 'ketchup', 'кетчуп', '[ˈketʃəp]', 'noun', 'A1', 'Pass the ketchup, please.'),
    ('food_shopping', 'last name', 'фамилия', '[læst neɪm]', 'phrase', 'A1', "What's your last name?"),
    ('food_shopping', 'lemon soda', 'лимонная газировка', '[ˈlemən ˈsoʊdə]', 'phrase', 'A2', "I'd like a lemon soda."),
    ('food_shopping', 'lemonade', 'лимонад', '[ˌleməˈneɪd]', 'noun', 'A1', 'We drank lemonade in the garden.'),
    ('food_shopping', 'lime soda', 'лаймовая газировка', '[laɪm ˈsoʊdə]', 'phrase', 'A2', 'A lime soda, please.'),
    ('food_shopping', 'liter', 'литр', '[ˈliːtər]', 'noun', 'A2', 'Buy a liter of water.'),
    ('food_shopping', 'milk', 'молоко', '[mɪlk]', 'noun', 'A1', 'I drink milk every morning.'),
    ('food_shopping', 'mustard', 'горчица', '[ˈmʌstərd]', 'noun', 'A2', 'Add some mustard to the sandwich.'),
    ('food_shopping', 'orange soda', 'апельсиновая газировка', '[ˈɔːrɪndʒ ˈsoʊdə]', 'phrase', 'A2', 'One orange soda, please.'),
    ('food_shopping', 'phone book', 'телефонный справочник', '[foʊn bʊk]', 'phrase', 'A2', 'Look it up in the phone book.'),
    ('food_shopping', 'pint (= 0.470 liters)', 'пинта', '[paɪnt]', 'noun', 'A2', 'A pint of milk, please.'),
    ('food_shopping', 'request', 'просьба', '[rɪˈkwest]', 'noun', 'A2', 'May I make a request?'),
    ('food_shopping', 'salad dressing', 'салатная приправа, соус', '[ˈsæləd ˈdresɪŋ]', 'phrase', 'A2', 'Pass the salad dressing, please.'),
    ('food_shopping', 'salt', 'соль', '[sɔːlt]', 'noun', 'A1', 'Pass the salt, please.'),
    ('food_shopping', 'soda', 'газировка', '[ˈsoʊdə]', 'noun', 'A1', "I'd like a soda."),
    ('food_shopping', 'straw', 'соломинка', '[strɔː]', 'noun', 'A1', 'Can I have a straw?'),
    ('food_shopping', 'sweetener', 'заменитель сахара', '[ˈswiːtnər]', 'noun', 'A2', 'Do you have any sweetener?'),
    ('food_shopping', 'tea', 'чай', '[tiː]', 'noun', 'A1', 'I drink tea every morning.'),
    ('food_shopping', 'phone number', 'телефонный номер', '[foʊn ˈnʌmbər]', 'phrase', 'A1', "What's your phone number?"),

    # --- Clothes & colors ---
    ('clothes_colors', 'apron', 'фартук', '[ˈeɪprən]', 'noun', 'A2', 'She wore an apron in the kitchen.'),
    ('clothes_colors', 'baseball player', 'бейсболист', '[ˈbeɪsbɔːl ˈpleɪər]', 'phrase', 'A2', 'He is a baseball player.'),
    ('clothes_colors', 'bay', 'залив, бухта', '[beɪ]', 'noun', 'A2', 'The boats are in the bay.'),
    ('clothes_colors', 'beach', 'пляж', '[biːtʃ]', 'noun', 'A1', 'We spent the day at the beach.'),
    ('clothes_colors', 'blouse', 'блузка, кофта', '[blaʊs]', 'noun', 'A2', 'She bought a new blouse.'),
    ('clothes_colors', 'boots', 'ботинки, сапоги', '[buːts]', 'noun', 'A1', "Wear your boots, it's snowing."),
    ('clothes_colors', 'cap', 'кепка, шапка', '[kæp]', 'noun', 'A1', 'He wears a baseball cap.'),
    ('clothes_colors', 'cape', 'накидка, плащ с капюшоном', '[keɪp]', 'noun', 'A2', 'The superhero wore a cape.'),
    ('clothes_colors', 'clothes', 'одежда', '[kloʊðz]', 'noun', 'A1', 'Put away your clothes.'),
    ('clothes_colors', 'color', 'цвет', '[ˈkʌlər]', 'noun', 'A1', 'What color do you like?'),
    ('clothes_colors', 'fire fighter', 'пожарник', '[ˈfaɪər ˌfaɪtər]', 'phrase', 'A1', 'The fire fighter saved the cat.'),
    ('clothes_colors', 'gloves', 'перчатки', '[ɡlʌvz]', 'noun', 'A1', "Wear gloves, it's cold."),
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
# The rest (Дом и кухня, Прилагательные, Глаголы, Другие слова) predate this
# migration and must not be removed on reverse — only unlinked.
NEW_DECK_KEYS = {'jobs_hotel', 'food_shopping', 'clothes_colors', 'phrases'}


def remove_words(apps, schema_editor):
    Deck = apps.get_model('vocabulary', 'Deck')
    Word = apps.get_model('vocabulary', 'Word')

    all_texts = [w[1] for w in WORDS]
    Word.objects.filter(language__code='en', owner__isnull=True, text__in=all_texts).delete()

    new_deck_names = [DECKS[k][0] for k in NEW_DECK_KEYS]
    Deck.objects.filter(owner__isnull=True, language__code='en', name__in=new_deck_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('vocabulary', '0007_seed_extended_english_vocabulary'),
    ]

    operations = [
        migrations.RunPython(seed_words, remove_words),
    ]
