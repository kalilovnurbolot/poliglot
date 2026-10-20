from django.db import migrations

# Where the first missions sit on the map, with a hook for each.
PLACES = {
    'В магазине': (14, 78, 'Первый день в Лондоне. Ваш багаж прилетит только вечером, а холодильник в номере пуст.'),
    'В кафе': (32, 60, 'Кофе перед поездкой в аэропорт. Бариста почему-то смотрит на вас слишком внимательно…'),
    'В пекарне': (50, 55, 'Первое утро в Берлине. Пахнет свежим хлебом — самое время для разговора.'),
}

# "Пропавший чемодан": a detective story in five chapters after the first two missions.
STORY = [
    {
        'level': 'A1', 'order': 3, 'scene': 'airport', 'npc_name': 'Сотрудница аэропорта',
        'map_x': 15, 'map_y': 25,
        'title': 'Пропавший чемодан',
        'teaser': 'Ваш красный чемодан прилетел — и тут же исчез с ленты. Кто-то видел человека в чёрной шляпе…',
        'briefing': 'Заявите о пропаже: назовите себя, опишите чемодан и скажите, где вы живёте.',
        'target_words': ['suitcase', 'lost', 'red', 'big', 'hotel'],
        'retry_line': 'Sorry, can you say that again, please?',
        'farewell_line': 'Be careful. That man in the black hat looked very strange…',
        'steps': [
            ('Hello. Lost and found. How can I help you?', 'Здравствуйте. Бюро находок. Чем могу помочь?',
             'Скажите, что потеряли чемодан', [['suitcase', 'bag', 'luggage'], ['lost', 'lose', 'missing', 'can not find']],
             ['Hello, I lost my suitcase.', 'My bag is missing.']),
            ('I am sorry to hear that. What is your name?', 'Сочувствую. Как вас зовут?',
             'Назовите своё имя', [['my name', 'i am', 'name is']],
             ['My name is Anna.', 'I am Max Petrov.']),
            ('What colour is your suitcase?', 'Какого цвета ваш чемодан?',
             'Скажите, что он большой и красный', [['red'], ['big', 'large']],
             ['It is big and red.', 'A big red suitcase.']),
            ('Hmm… A man in a black hat took a big red suitcase ten minutes ago. Where are you staying?',
             'Хм… Десять минут назад мужчина в чёрной шляпе забрал большой красный чемодан. Где вы остановились?',
             'Скажите, что живёте в отеле «Ривер»', [['hotel'], ['river']],
             ['I am staying at the River Hotel.', 'At the River Hotel.']),
            ('OK. We will call you at the hotel.', 'Хорошо. Мы позвоним вам в отель.',
             'Поблагодарите и попрощайтесь', [['thank', 'thanks'], ['bye', 'goodbye']],
             ['Thank you, goodbye!', 'Thanks a lot, bye!']),
        ],
    },
    {
        'level': 'A1', 'order': 4, 'scene': 'hotel', 'npc_name': 'Администратор',
        'map_x': 44, 'map_y': 22,
        'title': 'Записка без подписи',
        'teaser': 'Администратор отеля прячет глаза и протягивает вам конверт. Внутри — одна строчка и время.',
        'briefing': 'Возьмите ключ от номера и выясните, кто оставил записку и куда вас зовут.',
        'target_words': ['key', 'room', 'letter', 'who', 'where'],
        'retry_line': 'I am sorry, I did not understand. Could you repeat that?',
        'farewell_line': 'Good luck… and lock your door tonight.',
        'steps': [
            ('Good evening! Welcome back to the River Hotel.', 'Добрый вечер! С возвращением в отель «Ривер».',
             'Попросите ключ от номера', [['key']],
             ['Good evening. Can I have my key, please?', 'Hello, my room key, please.']),
            ('Of course. What is your room number?', 'Конечно. Какой у вас номер?',
             'Скажите: номер двенадцать', [['twelve', '12']],
             ['Room twelve.', 'My room is number twelve.']),
            ('Here you are. Oh… a man left this letter for you.', 'Пожалуйста. Ой… мужчина оставил для вас письмо.',
             'Спросите, кто этот мужчина', [['who']],
             ['Who is he?', 'Who left the letter?']),
            ('He wore a black hat. The letter says: «Café Luna. Five o’clock. Come alone.»',
             'Он был в чёрной шляпе. В письме: «Кафе „Луна“. Пять часов. Приходите один».',
             'Спросите, где находится кафе', [['where'], ['cafe', 'café', 'luna']],
             ['Where is Café Luna?', 'Where is the cafe, please?']),
            ('It is near the bridge. Go left, then straight on.', 'Это у моста. Идите налево, потом прямо.',
             'Поблагодарите администратора', [['thank', 'thanks']],
             ['Thank you very much!', 'Thanks for your help.']),
        ],
    },
    {
        'level': 'A2', 'order': 1, 'scene': 'cafe', 'npc_name': 'Незнакомец в шляпе',
        'map_x': 60, 'map_y': 48,
        'title': 'Встреча в кафе «Луна»',
        'teaser': 'Ровно пять. За угловым столиком — чёрная шляпа и газета. Под столом стоит ваш чемодан.',
        'briefing': 'Поговорите с незнакомцем: узнайте, где ваш чемодан и что в нём нашли.',
        'target_words': ['tea', 'where', 'suitcase', 'camera', 'police'],
        'retry_line': 'Speak clearly. We do not have much time.',
        'farewell_line': 'Hurry. And do not look back.',
        'steps': [
            ('You came. Sit down. Do you want something to drink?', 'Вы пришли. Садитесь. Хотите что-нибудь выпить?',
             'Попросите чай', [['tea', 'coffee', 'water']],
             ['Yes, a cup of tea, please.', 'Just some tea, please.']),
            ('Listen. I did not steal your bag. Someone put it on my trolley… by mistake. Or not by mistake.',
             'Послушайте. Я не крал вашу сумку. Кто-то поставил её на мою тележку… по ошибке. А может, и нет.',
             'Спросите, где сейчас ваш чемодан', [['where'], ['suitcase', 'bag', 'luggage']],
             ['Where is my suitcase now?', 'So where is my bag?']),
            ('It is safe, under the table. But I opened it. There was a camera inside. It is not yours, is it?',
             'Он в безопасности, под столом. Но я его открыл. Внутри была камера. Она ведь не ваша?',
             'Скажите, что это не ваша камера', [['camera'], ['not', 'no', 'never']],
             ['No, it is not my camera.', 'I do not have a camera.']),
            ('I knew it. Someone uses tourists to carry things. We must go to the police.',
             'Я так и знал. Кто-то использует туристов, чтобы перевозить вещи. Нам надо в полицию.',
             'Согласитесь и спросите, когда идти', [['when']],
             ['OK. When do we go?', 'Yes, you are right. When?']),
            ('Now. The police station is across the river. Follow me.', 'Сейчас же. Полиция на том берегу. Идите за мной.',
             'Скажите, что идёте с ним', [['go', 'come', 'follow', 'ready']],
             ["OK, let's go!", 'I am ready. I will follow you.']),
        ],
    },
    {
        'level': 'A2', 'order': 2, 'scene': 'police', 'npc_name': 'Инспектор Грей',
        'map_x': 80, 'map_y': 72,
        'title': 'Допрос у инспектора',
        'teaser': 'Инспектор Грей не верит ни вам, ни незнакомцу. А камера сняла кое-что очень интересное.',
        'briefing': 'Расскажите инспектору, что случилось, и вспомните, кого вы видели рядом с чемоданом.',
        'target_words': ['airport', 'yesterday', 'camera', 'woman', 'green'],
        'retry_line': 'Again, please. Slowly and clearly.',
        'farewell_line': 'Come to the museum tonight. We need your eyes.',
        'steps': [
            ('Sit down. Tell me what happened.', 'Садитесь. Расскажите, что случилось.',
             'Скажите, что ваш чемодан пропал в аэропорту', [['suitcase', 'bag', 'luggage'], ['airport']],
             ['My suitcase disappeared at the airport.', 'I lost my bag at the airport.']),
            ('When did you arrive in London?', 'Когда вы прилетели в Лондон?',
             'Скажите, что прилетели вчера', [['yesterday']],
             ['I arrived yesterday.', 'Yesterday morning.']),
            ('And this camera. Is it yours?', 'А эта камера — ваша?',
             'Скажите, что камера не ваша', [['not', 'no']],
             ['No, it is not mine.', 'No, it is not my camera.']),
            ('The camera filmed the diamond room at the museum. Did you see anyone near your bag?',
             'Камера снимала зал с бриллиантом в музее. Вы видели кого-нибудь рядом со своей сумкой?',
             'Скажите, что видели женщину в зелёном пальто', [['woman', 'lady', 'girl'], ['green']],
             ['I saw a woman in a green coat.', 'Yes, a lady in a green coat.']),
            ('A green coat… She works at the museum. You helped a lot.', 'Зелёное пальто… Она работает в музее. Вы очень помогли.',
             'Спросите, можно ли забрать чемодан', [['can', 'may', 'could'], ['suitcase', 'bag', 'luggage']],
             ['Can I take my suitcase now?', 'May I have my bag back, please?']),
        ],
    },
    {
        'level': 'A2', 'order': 3, 'scene': 'museum', 'npc_name': 'Охранник',
        'map_x': 84, 'map_y': 24,
        'title': 'Ночь в музее',
        'teaser': 'Финал. Сегодня ночью кто-то попробует украсть бриллиант. Полиция опаздывает — успеть можете только вы.',
        'briefing': 'Убедите охранника впустить вас, найдите зал с бриллиантом и остановите вора.',
        'target_words': ['police', 'diamond', 'steal', 'stop', 'suitcase'],
        'retry_line': 'What? Speak up, I cannot hear you!',
        'farewell_line': 'Your suitcase is waiting for you. Welcome to London, detective!',
        'steps': [
            ('The museum is closed! What do you want?', 'Музей закрыт! Что вам нужно?',
             'Скажите, что вас прислала полиция', [['police', 'inspector']],
             ['The police sent me.', 'Inspector Grey sent me.']),
            ('The police? OK… What do you need?', 'Полиция? Ладно… Что вам нужно?',
             'Спросите, где зал с бриллиантом', [['where'], ['diamond']],
             ['Where is the diamond room?', 'Where is the diamond, please?']),
            ('On the second floor. But why?', 'На втором этаже. Но зачем?',
             'Скажите, что кто-то хочет его украсть', [['steal', 'rob', 'take']],
             ['Someone wants to steal it!', 'A woman wants to take the diamond!']),
            ('Look! A woman in a green coat is running to the door!', 'Смотрите! Женщина в зелёном пальто бежит к двери!',
             'Крикните, чтобы она остановилась', [['stop']],
             ['Stop! Police!', 'Stop her!']),
            ('We got her! You are a hero! How can we thank you?', 'Попалась! Вы герой! Как нам вас отблагодарить?',
             'Скажите, что хотите просто получить свой чемодан', [['suitcase', 'bag', 'luggage']],
             ['Just give me my suitcase, please!', 'I only want my bag back.']),
        ],
    },
]


def seed_story(apps, schema_editor):
    Language = apps.get_model('core', 'Language')
    Mission = apps.get_model('missions', 'Mission')
    MissionStep = apps.get_model('missions', 'MissionStep')
    for title, (x, y, teaser) in PLACES.items():
        Mission.objects.filter(title=title).update(map_x=x, map_y=y, teaser=teaser)
    language = Language.objects.filter(code='en').first()
    if language is None:
        return
    for data in STORY:
        data = dict(data)
        steps = data.pop('steps')
        mission = Mission.objects.create(language=language, **data)
        for order, (npc_line, npc_line_ru, goal, keywords, patterns) in enumerate(steps, start=1):
            MissionStep.objects.create(
                mission=mission, order=order, npc_line=npc_line, npc_line_ru=npc_line_ru,
                goal=goal, keywords=keywords, patterns=patterns,
            )


def remove_story(apps, schema_editor):
    Mission = apps.get_model('missions', 'Mission')
    Mission.objects.filter(title__in=[m['title'] for m in STORY]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('missions', '0003_mission_map'),
    ]

    operations = [
        migrations.RunPython(seed_story, remove_story),
    ]
