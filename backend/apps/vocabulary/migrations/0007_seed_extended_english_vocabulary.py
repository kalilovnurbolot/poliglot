from django.db import migrations

# Decks: key -> (name, description)
DECKS = {
    'verbs': ('Глаголы', 'Самые частые английские глаголы.'),
    'people_life': ('Люди и жизнь', 'Базовые существительные о людях и жизни.'),
    'adjectives': ('Прилагательные', 'Базовые прилагательные для описания.'),
    'fruits': ('Фрукты', 'Названия фруктов.'),
    'vegetables': ('Овощи', 'Названия овощей.'),
    'home_kitchen': ('Дом и кухня', 'Немного бытовой лексики.'),
    'animals': ('Животные', 'Названия животных.'),
    'misc': ('Другие слова', 'Числа, наречия и другие частые слова.'),
}

# (deck_key, text, translation, transcription, part_of_speech, level, example_sentence)
WORDS = [
    # --- Verbs ---
    ('verbs', 'to be', 'быть', '[tuː biː]', 'verb', 'A1', 'I want to be a doctor.'),
    ('verbs', 'to have', 'иметь', '[tuː hæv]', 'verb', 'A1', 'I have two brothers.'),
    ('verbs', 'to do', 'делать', '[tuː duː]', 'verb', 'A1', 'What do you do on weekends?'),
    ('verbs', 'to say', 'сказать', '[tuː seɪ]', 'verb', 'A1', "She didn't say a word."),
    ('verbs', 'to go', 'идти', '[tuː ɡoʊ]', 'verb', 'A1', "Let's go to the park."),
    ('verbs', 'to get', 'получать', '[tuː ɡet]', 'verb', 'A1', 'Did you get my message?'),
    ('verbs', 'to know', 'знать', '[tuː noʊ]', 'verb', 'A1', 'I know the answer.'),
    ('verbs', 'to think', 'думать', '[tuː θɪŋk]', 'verb', 'A1', "I think you're right."),
    ('verbs', 'to take', 'брать', '[tuː teɪk]', 'verb', 'A1', 'Take my hand.'),
    ('verbs', 'to see', 'видеть', '[tuː siː]', 'verb', 'A1', 'I can see the mountains from here.'),
    ('verbs', 'to come', 'приходить', '[tuː kʌm]', 'verb', 'A1', 'Come here, please.'),
    ('verbs', 'to want', 'хотеть', '[tuː wɒnt]', 'verb', 'A1', 'I want a cup of tea.'),
    ('verbs', 'to look', 'смотреть', '[tuː lʊk]', 'verb', 'A1', 'Look at that beautiful sunset.'),
    ('verbs', 'to use', 'использовать', '[tuː juːz]', 'verb', 'A1', 'You can use my pen.'),
    ('verbs', 'to find', 'находить', '[tuː faɪnd]', 'verb', 'A1', "I can't find my keys."),
    ('verbs', 'to give', 'давать', '[tuː ɡɪv]', 'verb', 'A1', 'Can you give me the book?'),
    ('verbs', 'to tell', 'рассказывать', '[tuː tel]', 'verb', 'A1', 'Tell me a story.'),
    ('verbs', 'to work', 'работать', '[tuː wɜːrk]', 'verb', 'A1', 'I work in a bank.'),
    ('verbs', 'to cook', 'готовить', '[tuː kʊk]', 'verb', 'A1', 'My mother cooks dinner every day.'),
    ('verbs', 'to call', 'звонить; называть', '[tuː kɔːl]', 'verb', 'A1', "I'll call you tomorrow."),
    ('verbs', 'to try', 'пытаться; пробовать', '[tuː traɪ]', 'verb', 'A1', "Try this cake, it's delicious."),
    ('verbs', 'to ask', 'спрашивать; просить', '[tuː æsk]', 'verb', 'A1', 'Can I ask you a question?'),
    ('verbs', 'to need', 'нуждаться', '[tuː niːd]', 'verb', 'A1', 'I need some help.'),
    ('verbs', 'to feel', 'чувствовать', '[tuː fiːl]', 'verb', 'A1', 'I feel tired today.'),
    ('verbs', 'to become', 'становиться', '[tuː bɪˈkʌm]', 'verb', 'A2', 'She wants to become a teacher.'),
    ('verbs', 'to leave', 'покидать', '[tuː liːv]', 'verb', 'A1', 'The train leaves at noon.'),
    ('verbs', 'to put', 'класть', '[tuː pʊt]', 'verb', 'A1', 'Put the book on the table.'),
    ('verbs', 'to mean', 'иметь в виду', '[tuː miːn]', 'verb', 'A2', 'What do you mean?'),
    ('verbs', 'to keep', 'хранить', '[tuː kiːp]', 'verb', 'A1', 'Keep this secret.'),
    ('verbs', 'to let', 'позволять', '[tuː let]', 'verb', 'A1', 'Let me help you.'),
    ('verbs', 'to begin', 'начинать', '[tuː bɪˈɡɪn]', 'verb', 'A1', 'The movie begins at eight.'),
    ('verbs', 'to seem', 'казаться', '[tuː siːm]', 'verb', 'A2', 'It seems difficult.'),
    ('verbs', 'to help', 'помогать', '[tuː help]', 'verb', 'A1', 'Can you help me, please?'),
    ('verbs', 'to speak', 'говорить', '[tuː spiːk]', 'verb', 'A1', 'Do you speak English?'),
    ('verbs', 'to turn', 'поворачивать', '[tuː tɜːrn]', 'verb', 'A1', 'Turn left at the corner.'),
    ('verbs', 'to show', 'показывать', '[tuː ʃoʊ]', 'verb', 'A1', 'Show me your homework.'),
    ('verbs', 'to hear', 'слышать', '[tuː hɪr]', 'verb', 'A1', "I can't hear you."),
    ('verbs', 'to play', 'играть', '[tuː pleɪ]', 'verb', 'A1', 'Children love to play outside.'),
    ('verbs', 'to run', 'бежать', '[tuː rʌn]', 'verb', 'A1', 'He runs every morning.'),
    ('verbs', 'to move', 'двигаться', '[tuː muːv]', 'verb', 'A1', 'Please move your car.'),
    ('verbs', 'to like', 'нравиться; любить', '[tuː laɪk]', 'verb', 'A1', 'I like this song.'),
    ('verbs', 'to live', 'жить', '[tuː lɪv]', 'verb', 'A1', 'They live in a small town.'),
    ('verbs', 'to believe', 'верить', '[tuː bɪˈliːv]', 'verb', 'A2', 'I believe you.'),
    ('verbs', 'to hold', 'держать', '[tuː hoʊld]', 'verb', 'A1', 'Hold my hand.'),
    ('verbs', 'to eat', 'есть; кушать', '[tuː iːt]', 'verb', 'A1', 'We eat dinner at 7 pm.'),
    ('verbs', 'to bring', 'приносить', '[tuː brɪŋ]', 'verb', 'A1', 'Bring your umbrella, it might rain.'),
    ('verbs', 'to happen', 'случаться', '[tuː ˈhæpən]', 'verb', 'A2', 'What happened here?'),
    ('verbs', 'to write', 'писать', '[tuː raɪt]', 'verb', 'A1', 'Write your name here.'),
    ('verbs', 'to sit', 'сидеть', '[tuː sɪt]', 'verb', 'A1', 'Please sit down.'),
    ('verbs', 'to stand', 'стоять', '[tuː stænd]', 'verb', 'A1', 'Stand up, please.'),
    ('verbs', 'to lose', 'терять; проигрывать', '[tuː luːz]', 'verb', 'A2', "Don't lose your ticket."),
    ('verbs', 'to pay', 'платить', '[tuː peɪ]', 'verb', 'A1', "I'll pay for the tickets."),
    ('verbs', 'to meet', 'встречать(ся)', '[tuː miːt]', 'verb', 'A1', 'Nice to meet you.'),
    ('verbs', 'to continue', 'продолжать', '[tuː kənˈtɪnjuː]', 'verb', 'A2', 'Please continue reading.'),
    ('verbs', 'to study', 'учиться; изучать', '[tuː ˈstʌdi]', 'verb', 'A1', 'I study English every day.'),
    ('verbs', 'to change', 'менять', '[tuː tʃeɪndʒ]', 'verb', 'A1', 'I need to change my plans.'),
    ('verbs', 'to understand', 'понимать', '[tuː ˌʌndərˈstænd]', 'verb', 'A2', 'I understand you.'),
    ('verbs', 'to stop', 'останавливать; прекращать', '[tuː stɒp]', 'verb', 'A1', 'Stop the car!'),
    ('verbs', 'to create', 'создавать', '[tuː kriˈeɪt]', 'verb', 'A2', 'Artists create beautiful things.'),
    ('verbs', 'to read', 'читать', '[tuː riːd]', 'verb', 'A1', 'I like to read books.'),
    ('verbs', 'to spend', 'тратить', '[tuː spend]', 'verb', 'A2', "Don't spend too much money."),
    ('verbs', 'to grow', 'расти', '[tuː ɡroʊ]', 'verb', 'A1', 'Children grow up fast.'),
    ('verbs', 'to open', 'открывать', '[tuː ˈoʊpən]', 'verb', 'A1', 'Open the window, please.'),
    ('verbs', 'to win', 'побеждать', '[tuː wɪn]', 'verb', 'A1', 'Our team won the match.'),
    ('verbs', 'to offer', 'предлагать', '[tuː ˈɒfər]', 'verb', 'A2', 'She offered me some coffee.'),
    ('verbs', 'to remember', 'помнить', '[tuː rɪˈmembər]', 'verb', 'A1', 'I remember your name.'),
    ('verbs', 'to include', 'включать в себя', '[tuː ɪnˈkluːd]', 'verb', 'A2', 'The price includes breakfast.'),
    ('verbs', 'to appear', 'появляться', '[tuː əˈpɪr]', 'verb', 'A2', 'A new star appeared in the sky.'),
    ('verbs', 'to buy', 'покупать', '[tuː baɪ]', 'verb', 'A1', 'I want to buy a new phone.'),
    ('verbs', 'to wait', 'ждать', '[tuː weɪt]', 'verb', 'A1', 'Wait for me here.'),
    ('verbs', 'to serve', 'обслуживать', '[tuː sɜːrv]', 'verb', 'A2', 'This restaurant serves great food.'),
    ('verbs', 'to die', 'умирать', '[tuː daɪ]', 'verb', 'A2', 'Plants die without water.'),
    ('verbs', 'to send', 'отправлять', '[tuː send]', 'verb', 'A1', 'Send me an email.'),
    ('verbs', 'to build', 'строить', '[tuː bɪld]', 'verb', 'A1', 'They are building a new house.'),
    ('verbs', 'to drink', 'пить', '[tuː drɪŋk]', 'verb', 'A1', 'I drink coffee every morning.'),
    ('verbs', 'to stay', 'оставаться', '[tuː steɪ]', 'verb', 'A1', 'Stay here with me.'),
    ('verbs', 'to fall', 'падать', '[tuː fɔːl]', 'verb', 'A1', "Be careful, don't fall."),
    ('verbs', 'to cut', 'резать', '[tuː kʌt]', 'verb', 'A1', 'Cut the paper with scissors.'),
    ('verbs', 'to achieve', 'достигать', '[tuː əˈtʃiːv]', 'verb', 'A2', 'She achieved her goal.'),
    ('verbs', 'to kill', 'убивать', '[tuː kɪl]', 'verb', 'A2', 'The frost killed the plants.'),
    ('verbs', 'to suppose', 'предполагать', '[tuː səˈpoʊz]', 'verb', 'A2', "I suppose you're right."),
    ('verbs', 'to require', 'требовать', '[tuː rɪˈkwaɪər]', 'verb', 'A2', 'This job requires patience.'),
    ('verbs', 'to hide', 'прятать(ся)', '[tuː haɪd]', 'verb', 'A2', 'The cat is hiding under the bed.'),
    ('verbs', 'to forget', 'забывать', '[tuː fərˈɡet]', 'verb', 'A1', "Don't forget your keys."),
    ('verbs', 'can', 'мочь', '[kæn]', 'verb', 'A1', 'I can swim.'),
    ('verbs', 'to answer', 'отвечать', '[tuː ˈænsər]', 'verb', 'A1', 'Answer the question, please.'),
    ('verbs', 'to notice', 'замечать', '[tuː ˈnoʊtɪs]', 'verb', 'A2', "I noticed a change in her mood."),
    ('verbs', 'to sleep', 'спать', '[tuː sliːp]', 'verb', 'A1', 'Babies sleep a lot.'),
    ('verbs', 'to close', 'закрывать', '[tuː kloʊz]', 'verb', 'A1', 'Close the door, please.'),
    ('verbs', 'to fly', 'летать', '[tuː flaɪ]', 'verb', 'A1', 'Birds fly south in winter.'),
    ('verbs', 'to breathe', 'дышать', '[tuː briːð]', 'verb', 'A2', 'Breathe deeply.'),
    ('verbs', 'to get dressed', 'одеваться', '[tuː ɡet drest]', 'verb', 'A1', 'He gets dressed quickly.'),
    ('verbs', 'to earn', 'зарабатывать', '[tuː ɜːrn]', 'verb', 'A2', 'She earns a good salary.'),
    ('verbs', 'to rest', 'отдыхать', '[tuː rest]', 'verb', 'A1', 'You should rest after work.'),
    ('verbs', 'to wash', 'мыть', '[tuː wɒʃ]', 'verb', 'A1', 'Wash your hands before eating.'),
    ('verbs', 'to celebrate', 'праздновать', '[tuː ˈselɪbreɪt]', 'verb', 'A2', "We celebrate her birthday every year."),

    # --- People & life ---
    ('people_life', 'person', 'человек', '[ˈpɜːrsən]', 'noun', 'A1', 'There is a person at the door.'),
    ('people_life', 'people', 'люди', '[ˈpiːpəl]', 'noun', 'A1', 'There are many people here.'),
    ('people_life', 'day', 'день', '[deɪ]', 'noun', 'A1', 'Have a nice day!'),
    ('people_life', 'man', 'мужчина', '[mæn]', 'noun', 'A1', 'That man is my uncle.'),
    ('people_life', 'men', 'мужчины', '[men]', 'noun', 'A1', 'The men are working outside.'),
    ('people_life', 'woman', 'женщина', '[ˈwʊmən]', 'noun', 'A1', 'She is a kind woman.'),
    ('people_life', 'women', 'женщины', '[ˈwɪmɪn]', 'noun', 'A1', 'The women are talking.'),
    ('people_life', 'child', 'ребёнок', '[tʃaɪld]', 'noun', 'A1', 'The child is playing.'),
    ('people_life', 'children', 'дети', '[ˈtʃɪldrən]', 'noun', 'A1', 'The children are laughing.'),
    ('people_life', 'thing', 'вещь', '[θɪŋ]', 'noun', 'A1', 'What is this thing?'),
    ('people_life', 'time', 'время', '[taɪm]', 'noun', 'A1', 'What time is it?'),
    ('people_life', 'year', 'год', '[jɪr]', 'noun', 'A1', 'See you next year.'),
    ('people_life', 'life', 'жизнь', '[laɪf]', 'noun', 'A1', 'Life is beautiful.'),
    ('people_life', 'way', 'путь', '[weɪ]', 'noun', 'A1', 'This is the way to the station.'),
    ('people_life', 'world', 'мир', '[wɜːrld]', 'noun', 'A1', 'The world is big.'),
    ('people_life', 'school', 'школа', '[skuːl]', 'noun', 'A1', 'I go to school every day.'),
    ('people_life', 'religion', 'религия', '[rɪˈlɪdʒən]', 'noun', 'A2', 'They study different religions.'),

    # --- Adjectives ---
    ('adjectives', 'good', 'хороший', '[ɡʊd]', 'adjective', 'A1', 'This is a good idea.'),
    ('adjectives', 'bad', 'плохой', '[bæd]', 'adjective', 'A1', 'This is a bad idea.'),
    ('adjectives', 'big', 'большой', '[bɪɡ]', 'adjective', 'A1', 'They bought a big car.'),
    ('adjectives', 'small', 'маленький', '[smɔːl]', 'adjective', 'A1', "It's a small room."),
    ('adjectives', 'tall', 'высокий', '[tɔːl]', 'adjective', 'A1', 'He is very tall.'),
    ('adjectives', 'low', 'низкий', '[loʊ]', 'adjective', 'A1', 'The table is low.'),
    ('adjectives', 'long', 'длинный', '[lɔːŋ]', 'adjective', 'A1', 'She has long hair.'),
    ('adjectives', 'short', 'короткий', '[ʃɔːrt]', 'adjective', 'A1', 'This is a short story.'),
    ('adjectives', 'new', 'новый', '[nuː]', 'adjective', 'A1', 'I bought a new car.'),
    ('adjectives', 'old', 'старый', '[oʊld]', 'adjective', 'A1', 'This is an old book.'),
    ('adjectives', 'young', 'молодой', '[jʌŋ]', 'adjective', 'A1', 'She is very young.'),
    ('adjectives', 'beautiful', 'красивый', '[ˈbjuːtɪfəl]', 'adjective', 'A1', 'What a beautiful garden!'),
    ('adjectives', 'ugly', 'некрасивый', '[ˈʌɡli]', 'adjective', 'A2', 'That painting is ugly.'),
    ('adjectives', 'happy', 'счастливый', '[ˈhæpi]', 'adjective', 'A1', 'She looks happy today.'),
    ('adjectives', 'sad', 'грустный', '[sæd]', 'adjective', 'A1', 'He looks sad today.'),
    ('adjectives', 'kind', 'добрый', '[kaɪnd]', 'adjective', 'A1', 'She is very kind.'),
    ('adjectives', 'mean', 'злой', '[miːn]', 'adjective', 'A2', "Don't be mean to your sister."),
    ('adjectives', 'strong', 'сильный', '[strɔːŋ]', 'adjective', 'A1', 'He is a strong man.'),
    ('adjectives', 'weak', 'слабый', '[wiːk]', 'adjective', 'A2', 'I feel weak after the flu.'),
    ('adjectives', 'fast', 'быстрый', '[fæst]', 'adjective', 'A1', 'This is a fast car.'),
    ('adjectives', 'slow', 'медленный', '[sloʊ]', 'adjective', 'A1', 'The internet is slow today.'),
    ('adjectives', 'easy', 'лёгкий', '[ˈiːzi]', 'adjective', 'A1', 'This exercise is easy.'),
    ('adjectives', 'difficult', 'трудный', '[ˈdɪfɪkəlt]', 'adjective', 'A2', 'This exercise is quite difficult.'),
    ('adjectives', 'important', 'важный', '[ɪmˈpɔːrtənt]', 'adjective', 'A2', 'This meeting is important.'),
    ('adjectives', 'interesting', 'интересный', '[ˈɪntrəstɪŋ]', 'adjective', 'A2', "That's an interesting story."),
    ('adjectives', 'boring', 'скучный', '[ˈbɔːrɪŋ]', 'adjective', 'A2', 'This movie is boring.'),
    ('adjectives', 'expensive', 'дорогой', '[ɪkˈspensɪv]', 'adjective', 'A2', 'That restaurant is too expensive.'),
    ('adjectives', 'cheap', 'дешёвый', '[tʃiːp]', 'adjective', 'A1', 'This restaurant is cheap.'),
    ('adjectives', 'rich', 'богатый', '[rɪtʃ]', 'adjective', 'A1', 'He is a rich businessman.'),
    ('adjectives', 'poor', 'бедный', '[pʊr]', 'adjective', 'A1', 'They were a poor family.'),
    ('adjectives', 'clean', 'чистый', '[kliːn]', 'adjective', 'A1', 'Keep your room clean.'),
    ('adjectives', 'dirty', 'грязный', '[ˈdɜːrti]', 'adjective', 'A1', 'Your shoes are dirty.'),
    ('adjectives', 'honest', 'честный', '[ˈɒnɪst]', 'adjective', 'A2', 'Please be honest with me.'),
    ('adjectives', 'smart', 'умный', '[smɑːrt]', 'adjective', 'A1', 'She is a smart student.'),
    ('adjectives', 'silly', 'глупый', '[ˈsɪli]', 'adjective', 'A1', "Don't be silly."),
    ('adjectives', 'healthy', 'здоровый', '[ˈhelθi]', 'adjective', 'A2', 'Eating vegetables is healthy.'),
    ('adjectives', 'sick', 'больной', '[sɪk]', 'adjective', 'A1', 'He is sick today.'),
    ('adjectives', 'hungry', 'голодный', '[ˈhʌŋɡri]', 'adjective', 'A1', 'I am very hungry.'),
    ('adjectives', 'tired', 'уставший', '[ˈtaɪəd]', 'adjective', 'A1', 'I am tired after work.'),
    ('adjectives', 'busy', 'занятый', '[ˈbɪzi]', 'adjective', 'A1', 'I am busy right now.'),
    ('adjectives', 'free', 'свободный', '[friː]', 'adjective', 'A1', 'Are you free tomorrow?'),
    ('adjectives', 'religious', 'религиозный', '[rɪˈlɪdʒəs]', 'adjective', 'A2', 'Her family is very religious.'),
    ('adjectives', 'confident', 'уверенный', '[ˈkɒnfɪdənt]', 'adjective', 'A2', 'She is a confident speaker.'),
    ('adjectives', 'self-confident', 'самоуверенный', '[self ˈkɒnfɪdənt]', 'adjective', 'A2', 'He is very self-confident.'),
    ('adjectives', 'tiny', 'крошечный', '[ˈtaɪni]', 'adjective', 'A1', 'The kitten is tiny.'),

    # --- Fruits ---
    ('fruits', 'apple', 'яблоко', '[ˈæpəl]', 'noun', 'A1', 'I eat an apple every day.'),
    ('fruits', 'banana', 'банан', '[bəˈnænə]', 'noun', 'A1', 'I eat a banana every morning.'),
    ('fruits', 'orange', 'апельсин', '[ˈɔːrɪndʒ]', 'noun', 'A1', 'She squeezed an orange for juice.'),
    ('fruits', 'tangerine', 'мандарин', '[ˌtændʒəˈriːn]', 'noun', 'A2', 'Tangerines are popular in winter.'),
    ('fruits', 'lemon', 'лимон', '[ˈlemən]', 'noun', 'A1', 'Add a slice of lemon to your tea.'),
    ('fruits', 'lime', 'лайм', '[laɪm]', 'noun', 'A2', 'The cocktail has lime juice.'),
    ('fruits', 'pomegranate', 'гранат', '[ˈpɒmɪɡrænɪt]', 'noun', 'A2', 'Pomegranate seeds are sweet and sour.'),
    ('fruits', 'strawberry', 'клубника', '[ˈstrɔːbəri]', 'noun', 'A1', 'We picked strawberries in the garden.'),
    ('fruits', 'raspberry', 'малина', '[ˈræzbəri]', 'noun', 'A1', 'Raspberry jam is delicious.'),
    ('fruits', 'currant', 'смородина', '[ˈkʌrənt]', 'noun', 'A2', 'She made currant juice.'),
    ('fruits', 'watermelon', 'арбуз', '[ˈwɔːtərmelən]', 'noun', 'A1', 'Watermelon is refreshing in summer.'),
    ('fruits', 'melon', 'дыня', '[ˈmelən]', 'noun', 'A1', 'This melon is very sweet.'),
    ('fruits', 'peach', 'персик', '[piːtʃ]', 'noun', 'A1', 'The peach is soft and juicy.'),
    ('fruits', 'pistachio', 'фисташка', '[pɪˈstɑːʃioʊ]', 'noun', 'A2', 'I love pistachio ice cream.'),
    ('fruits', 'apricot', 'абрикос', '[ˈeɪprɪkɒt]', 'noun', 'A2', 'Apricot jam is my favorite.'),
    ('fruits', 'plum', 'слива', '[plʌm]', 'noun', 'A1', 'The plum tree is full of fruit.'),
    ('fruits', 'cherry', 'вишня', '[ˈtʃeri]', 'noun', 'A1', 'Cherry pie is a classic dessert.'),
    ('fruits', 'pear', 'груша', '[per]', 'noun', 'A1', 'She ate a ripe pear.'),
    ('fruits', 'pineapple', 'ананас', '[ˈpaɪnæpəl]', 'noun', 'A1', 'Pineapple is great on pizza.'),
    ('fruits', 'coconut', 'кокос', '[ˈkoʊkənʌt]', 'noun', 'A1', 'Coconut milk is used in this recipe.'),
    ('fruits', 'dried fruits', 'сухофрукты', '[draɪd fruːts]', 'phrase', 'A2', 'Dried fruits are a healthy snack.'),

    # --- Vegetables ---
    ('vegetables', 'potato', 'картофель', '[pəˈteɪtoʊ]', 'noun', 'A1', 'Mash the potatoes.'),
    ('vegetables', 'tomato', 'помидор', '[təˈmeɪtoʊ]', 'noun', 'A1', 'The salad has fresh tomatoes.'),
    ('vegetables', 'cucumber', 'огурец', '[ˈkjuːkʌmbər]', 'noun', 'A1', 'Cucumbers are great in salads.'),
    ('vegetables', 'carrot', 'морковь', '[ˈkærət]', 'noun', 'A1', 'Rabbits love carrots.'),
    ('vegetables', 'onion', 'лук', '[ˈʌnjən]', 'noun', 'A1', 'Chop the onion finely.'),
    ('vegetables', 'garlic', 'чеснок', '[ˈɡɑːrlɪk]', 'noun', 'A1', 'Add two cloves of garlic.'),
    ('vegetables', 'cabbage', 'капуста', '[ˈkæbɪdʒ]', 'noun', 'A1', 'Cabbage soup is popular in winter.'),
    ('vegetables', 'pepper', 'перец', '[ˈpepər]', 'noun', 'A1', 'Add some pepper to the sauce.'),
    ('vegetables', 'eggplant', 'баклажан', '[ˈeɡplɑːnt]', 'noun', 'A2', 'Eggplant is used in many dishes.'),
    ('vegetables', 'pumpkin', 'тыква', '[ˈpʌmpkɪn]', 'noun', 'A1', 'We carve a pumpkin for Halloween.'),
    ('vegetables', 'salad', 'салат', '[ˈsæləd]', 'noun', 'A1', 'I had a salad for lunch.'),

    # --- Home & kitchen ---
    ('home_kitchen', 'pot', 'кастрюля', '[pɒt]', 'noun', 'A2', 'Put the pot on the stove.'),
    ('home_kitchen', 'sofa', 'диван', '[ˈsoʊfə]', 'noun', 'A1', 'They sat on the sofa.'),
    ('home_kitchen', 'frying pan', 'сковородка', '[ˈfraɪɪŋ pæn]', 'phrase', 'A2', 'Heat the oil in a frying pan.'),
    ('home_kitchen', 'armchair', 'кресло', '[ˈɑːrmtʃer]', 'noun', 'A2', 'He relaxed in his armchair.'),
    ('home_kitchen', 'equipment', 'оборудование', '[ɪˈkwɪpmənt]', 'noun', 'A2', 'The gym has new equipment.'),
    ('home_kitchen', 'oath', 'клятва', '[oʊθ]', 'noun', 'A2', 'He took an oath of loyalty.'),
    ('home_kitchen', 'promise', 'обещание', '[ˈprɒmɪs]', 'noun', 'A2', 'She kept her promise.'),

    # --- Animals ---
    ('animals', 'dog', 'собака', '[dɒɡ]', 'noun', 'A1', 'The dog is barking.'),
    ('animals', 'cat', 'кошка', '[kæt]', 'noun', 'A1', 'The cat is sleeping.'),
    ('animals', 'horse', 'лошадь', '[hɔːrs]', 'noun', 'A1', 'She rides a horse.'),
    ('animals', 'cow', 'корова', '[kaʊ]', 'noun', 'A1', 'The cow gives milk.'),
    ('animals', 'sheep', 'овца', '[ʃiːp]', 'noun', 'A1', 'Sheep live on the farm.'),
    ('animals', 'goat', 'коза', '[ɡoʊt]', 'noun', 'A1', 'The goat eats grass.'),
    ('animals', 'pig', 'свинья', '[pɪɡ]', 'noun', 'A1', 'The pig is in the mud.'),
    ('animals', 'rabbit', 'кролик', '[ˈræbɪt]', 'noun', 'A1', 'The rabbit has long ears.'),
    ('animals', 'mouse', 'мышь', '[maʊs]', 'noun', 'A1', 'A mouse ran across the floor.'),
    ('animals', 'rat', 'крыса', '[ræt]', 'noun', 'A1', 'Rats live in the city.'),
    ('animals', 'lion', 'лев', '[ˈlaɪən]', 'noun', 'A1', 'The lion is the king of the jungle.'),
    ('animals', 'tiger', 'тигр', '[ˈtaɪɡər]', 'noun', 'A1', 'The tiger has stripes.'),
    ('animals', 'elephant', 'слон', '[ˈelɪfənt]', 'noun', 'A1', 'The elephant is huge.'),
    ('animals', 'giraffe', 'жираф', '[dʒəˈræf]', 'noun', 'A1', 'The giraffe has a long neck.'),
    ('animals', 'monkey', 'обезьяна', '[ˈmʌŋki]', 'noun', 'A1', 'The monkey climbed the tree.'),
    ('animals', 'bear', 'медведь', '[ber]', 'noun', 'A1', 'The bear is sleeping in its cave.'),
    ('animals', 'wolf', 'волк', '[wʊlf]', 'noun', 'A2', 'The wolf howled at the moon.'),
    ('animals', 'fox', 'лиса', '[fɒks]', 'noun', 'A1', 'The fox is clever.'),
    ('animals', 'deer', 'олень', '[dɪr]', 'noun', 'A2', 'We saw a deer in the forest.'),
    ('animals', 'zebra', 'зебра', '[ˈziːbrə]', 'noun', 'A1', 'The zebra has black and white stripes.'),
    ('animals', 'kangaroo', 'кенгуру', '[ˌkæŋɡəˈruː]', 'noun', 'A1', 'The kangaroo jumps very high.'),
    ('animals', 'panda', 'панда', '[ˈpændə]', 'noun', 'A1', 'The panda eats bamboo.'),
    ('animals', 'koala', 'коала', '[koʊˈɑːlə]', 'noun', 'A1', 'The koala sleeps most of the day.'),
    ('animals', 'turtle', 'черепаха', '[ˈtɜːrtəl]', 'noun', 'A1', 'The turtle moves slowly.'),
    ('animals', 'snake', 'змея', '[sneɪk]', 'noun', 'A1', 'The snake has no legs.'),
    ('animals', 'crocodile', 'крокодил', '[ˈkrɒkədaɪl]', 'noun', 'A2', 'The crocodile lives near the river.'),
    ('animals', 'frog', 'лягушка', '[frɒɡ]', 'noun', 'A1', 'The frog jumped into the pond.'),
    ('animals', 'bird', 'птица', '[bɜːrd]', 'noun', 'A1', 'The bird is singing.'),
    ('animals', 'eagle', 'орёл', '[ˈiːɡəl]', 'noun', 'A2', 'The eagle flies high in the sky.'),
    ('animals', 'parrot', 'попугай', '[ˈpærət]', 'noun', 'A1', 'The parrot can talk.'),
    ('animals', 'chicken', 'курица', '[ˈtʃɪkɪn]', 'noun', 'A1', 'The chicken laid an egg.'),
    ('animals', 'duck', 'утка', '[dʌk]', 'noun', 'A1', 'The duck swims in the lake.'),
    ('animals', 'fish', 'рыба', '[fɪʃ]', 'noun', 'A1', 'Fish live in water.'),
    ('animals', 'dolphin', 'дельфин', '[ˈdɒlfɪn]', 'noun', 'A1', 'The dolphin is very smart.'),
    ('animals', 'whale', 'кит', '[weɪl]', 'noun', 'A1', 'The whale is the biggest animal.'),
    ('animals', 'shark', 'акула', '[ʃɑːrk]', 'noun', 'A1', 'The shark swims in the ocean.'),
    ('animals', 'butterfly', 'бабочка', '[ˈbʌtərflaɪ]', 'noun', 'A1', 'The butterfly landed on the flower.'),
    ('animals', 'bee', 'пчела', '[biː]', 'noun', 'A1', 'The bee makes honey.'),
    ('animals', 'ant', 'муравей', '[ænt]', 'noun', 'A1', 'Ants work together.'),
    ('animals', 'spider', 'паук', '[ˈspaɪdər]', 'noun', 'A1', 'The spider made a web.'),

    # --- Additional words ---
    ('misc', 'one', 'один', '[wʌn]', 'other', 'A1', 'I have one brother.'),
    ('misc', 'two', 'два', '[tuː]', 'other', 'A1', 'She has two cats.'),
    ('misc', 'other', 'другой', '[ˈʌðər]', 'other', 'A1', 'I like the other one better.'),
    ('misc', 'more', 'больше', '[mɔːr]', 'other', 'A1', 'I want more tea.'),
    ('misc', 'only', 'только', '[ˈoʊnli]', 'adverb', 'A1', 'She is the only student here.'),
    ('misc', 'very', 'очень', '[ˈveri]', 'adverb', 'A1', "It's very hot today."),
    ('misc', 'even', 'даже', '[ˈiːvən]', 'adverb', 'A2', 'Even a child can do this.'),
    ('misc', 'back', 'назад', '[bæk]', 'adverb', 'A1', 'Come back soon.'),
    ('misc', 'down', 'вниз', '[daʊn]', 'adverb', 'A1', 'Sit down, please.'),
    ('misc', 'there', 'там', '[ðer]', 'adverb', 'A1', 'There is a book on the table.'),
    ('misc', 'first', 'первый', '[fɜːrst]', 'adjective', 'A1', 'This is my first day at work.'),
    ('misc', 'last', 'последний', '[læst]', 'adjective', 'A1', 'This is the last chapter.'),
    ('misc', 'simply', 'просто', '[ˈsɪmpli]', 'adverb', 'A2', "It's simply amazing."),
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


# Texts that already existed before this migration (reused via get_or_create) —
# on reverse, only unlink them from the new decks instead of deleting the word.
PREEXISTING_TEXTS = {
    'to go', 'to speak', 'to eat', 'to buy', 'to understand',
    'good', 'big', 'happy', 'difficult', 'expensive', 'tired', 'apple', 'time',
}


def remove_words(apps, schema_editor):
    Deck = apps.get_model('vocabulary', 'Deck')
    Word = apps.get_model('vocabulary', 'Word')

    new_texts = [w[1] for w in WORDS if w[1] not in PREEXISTING_TEXTS]
    Word.objects.filter(language__code='en', owner__isnull=True, text__in=new_texts).delete()

    deck_names = [name for name, _ in DECKS.values()]
    decks = Deck.objects.filter(owner__isnull=True, language__code='en', name__in=deck_names)
    for word in Word.objects.filter(language__code='en', owner__isnull=True, text__in=PREEXISTING_TEXTS):
        word.decks.remove(*decks)
    decks.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('vocabulary', '0006_seed_a2_words'),
    ]

    operations = [
        migrations.RunPython(seed_words, remove_words),
    ]
