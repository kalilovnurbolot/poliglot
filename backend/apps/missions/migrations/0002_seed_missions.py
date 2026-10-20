from django.db import migrations

MISSIONS = [
    {
        'language': 'en', 'level': 'A1', 'order': 1, 'scene': 'shop', 'npc_name': 'Продавец',
        'title': 'В магазине',
        'briefing': 'Купите хлеб и молоко, узнайте цену и заплатите картой. Не забудьте быть вежливым.',
        'target_words': ['bread', 'milk', 'please', 'how much', 'card', 'thank you'],
        'retry_line': "Sorry, I didn't catch that. Could you say it again?",
        'farewell_line': 'You are welcome. Have a nice day!',
        'steps': [
            ('Hello! How can I help you?', 'Здравствуйте! Чем могу помочь?',
             'Поздоровайтесь и попросите хлеб', [['bread', 'loaf']],
             ['Hello, can I have some bread, please?', 'Hi, I would like a loaf of bread, please.']),
            ('Sure, here you go. Anything else?', 'Конечно, пожалуйста. Что-нибудь ещё?',
             'Попросите молоко', [['milk']],
             ['Yes, I would like some milk, please.', 'Can I have a bottle of milk, please?']),
            ('Of course. Is that everything?', 'Конечно. Это всё?',
             'Спросите, сколько это стоит', [['how much', 'price', 'cost']],
             ['Yes, how much is it?', 'That is all. How much does it cost?']),
            ('That is four dollars fifty.', 'С вас четыре доллара пятьдесят.',
             'Скажите, что заплатите картой', [['card']],
             ['Can I pay by card?', 'I will pay by card, please.']),
            ('No problem. Here is your receipt.', 'Без проблем. Вот ваш чек.',
             'Поблагодарите и попрощайтесь', [['thank', 'thanks'], ['bye', 'goodbye', 'nice day']],
             ['Thank you, goodbye!', 'Thanks, have a nice day!']),
        ],
    },
    {
        'language': 'en', 'level': 'A1', 'order': 2, 'scene': 'cafe', 'npc_name': 'Бариста',
        'title': 'В кафе',
        'briefing': 'Закажите большой кофе и кусок торта с собой, затем заплатите.',
        'target_words': ['coffee', 'large', 'cake', 'take away', 'please'],
        'retry_line': 'Sorry, could you repeat that, please?',
        'farewell_line': 'Enjoy your coffee! See you soon.',
        'steps': [
            ('Hi there! What can I get you?', 'Привет! Что вам предложить?',
             'Закажите кофе', [['coffee', 'latte', 'cappuccino']],
             ['Hi, can I have a coffee, please?', 'I would like a cup of coffee, please.']),
            ('Small or large?', 'Маленький или большой?',
             'Выберите большой размер', [['large', 'big']],
             ['Large, please.', 'A large one, please.']),
            ('Anything to eat?', 'Что-нибудь поесть?',
             'Попросите кусок торта', [['cake']],
             ['Yes, a piece of cake, please.', 'Can I have some cake, please?']),
            ('For here or to go?', 'Здесь или с собой?',
             'Скажите, что возьмёте с собой', [['take away', 'to go', 'takeaway']],
             ['To go, please.', 'Take away, please.']),
            ('That is seven dollars, please.', 'С вас семь долларов.',
             'Заплатите и поблагодарите', [['thank', 'thanks', 'here you are', 'here you go']],
             ['Here you are. Thank you!', 'Here you go, thanks!']),
        ],
    },
    {
        'language': 'de', 'level': 'A1', 'order': 1, 'scene': 'bakery', 'npc_name': 'Пекарь',
        'title': 'В пекарне',
        'briefing': 'Купите хлеб и две булочки, спросите цену и заплатите наличными.',
        'target_words': ['brot', 'brötchen', 'bitte', 'wie viel', 'bar', 'danke'],
        'retry_line': 'Wie bitte? Können Sie das wiederholen?',
        'farewell_line': 'Danke schön! Einen schönen Tag noch!',
        'steps': [
            ('Guten Tag! Was darf es sein?', 'Добрый день! Что желаете?',
             'Поздоровайтесь и попросите хлеб', [['brot']],
             ['Guten Tag, ich möchte ein Brot, bitte.', 'Hallo, ein Brot, bitte.']),
            ('Gerne. Noch etwas?', 'С удовольствием. Что-нибудь ещё?',
             'Попросите две булочки', [['brötchen'], ['zwei']],
             ['Ja, zwei Brötchen, bitte.', 'Ich hätte gern zwei Brötchen.']),
            ('Ist das alles?', 'Это всё?',
             'Спросите, сколько это стоит', [['wie viel', 'wieviel', 'was kostet', 'kostet']],
             ['Ja, wie viel kostet das?', 'Das ist alles. Was kostet das?']),
            ('Das macht drei Euro zwanzig.', 'С вас три евро двадцать.',
             'Скажите, что заплатите наличными', [['bar']],
             ['Ich zahle bar.', 'Ich möchte bar bezahlen.']),
            ('Hier ist Ihr Wechselgeld.', 'Вот ваша сдача.',
             'Поблагодарите и попрощайтесь', [['danke'], ['tschüss', 'wiedersehen', 'schönen tag']],
             ['Danke schön, auf Wiedersehen!', 'Danke, tschüss!']),
        ],
    },
]


def seed_missions(apps, schema_editor):
    Language = apps.get_model('core', 'Language')
    Mission = apps.get_model('missions', 'Mission')
    MissionStep = apps.get_model('missions', 'MissionStep')
    for data in MISSIONS:
        data = dict(data)
        steps = data.pop('steps')
        language = Language.objects.filter(code=data.pop('language')).first()
        if language is None:
            continue
        mission = Mission.objects.create(language=language, **data)
        for order, (npc_line, npc_line_ru, goal, keywords, patterns) in enumerate(steps, start=1):
            MissionStep.objects.create(
                mission=mission, order=order, npc_line=npc_line, npc_line_ru=npc_line_ru,
                goal=goal, keywords=keywords, patterns=patterns,
            )


def remove_missions(apps, schema_editor):
    Mission = apps.get_model('missions', 'Mission')
    Mission.objects.filter(title__in=[m['title'] for m in MISSIONS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('missions', '0001_initial'),
        ('core', '0003_seed_german_language'),
    ]

    operations = [
        migrations.RunPython(seed_missions, remove_missions),
    ]
