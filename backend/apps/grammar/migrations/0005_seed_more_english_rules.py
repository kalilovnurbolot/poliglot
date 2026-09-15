from django.db import migrations

RULES = [
    (
        'A1', 8, 'There is / There are',
        """Используется, чтобы сказать, что что-то существует или находится где-то.

- **There is** + существительное в единственном числе: *There **is** a book on the table.*
- **There are** + существительное во множественном числе: *There **are** two cats in the garden.*

Отрицание: *There **isn't** any milk. There **aren't** any apples.*

Вопрос: *Is there a shop nearby? Are there any children here?*""",
    ),
    (
        'A1', 9, 'Предлоги места in, on, at',
        """Три самых частых предлога места:

- **in** — внутри чего-то (в комнате, в городе, в стране): *in the room, in London, in the box*
- **on** — на поверхности: *on the table, on the wall, on the floor*
- **at** — у конкретной точки/адреса: *at the door, at school, at the bus stop*

Пример: *She is **at** school, **in** the classroom, sitting **on** a chair.*""",
    ),
    (
        'A1', 10, 'Some / any',
        """**some** и **any** означают "несколько/немного" и используются с исчисляемыми (во мн. числе) и неисчисляемыми существительными.

- **some** — в утвердительных предложениях: *I have **some** apples. I need **some** water.*
- **any** — в отрицаниях и вопросах: *I don't have **any** apples. Do you have **any** water?*

Исключение: в вопросах-предложениях (просьба, предложение) используется **some**: *Would you like **some** tea?*""",
    ),
    (
        'A2', 3, 'Сравнительная и превосходная степень прилагательных',
        """Чтобы сравнить два предмета — сравнительная степень; чтобы выделить один из многих — превосходная.

**Короткие прилагательные** (1 слог): **-er** / **-est**
- *tall → taller → the tallest*
- *big → bigger → the biggest* (удвоение согласной)

**Длинные прилагательные** (2+ слога): **more** / **the most**
- *interesting → more interesting → the most interesting*
- *expensive → more expensive → the most expensive*

**Исключения:**
- *good → better → the best*
- *bad → worse → the worst*

Пример: *This book is **more interesting than** that one, but the film is **the most interesting** of all.*""",
    ),
    (
        'A2', 4, 'Модальный глагол can',
        """**can** выражает способность (уметь), возможность и разрешение. После **can** глагол всегда в начальной форме без **to**.

- Способность: *I **can** swim.*
- Разрешение: *You **can** go now.*
- Просьба/вопрос: *Can you help me?*

Отрицание — **can't** (cannot): *She **can't** drive.*

У **can** нет форм на **-s** в 3-м лице: *He **can** speak French* (не canS).""",
    ),
    (
        'A2', 5, 'Оборот going to (будущее время)',
        """**be going to** используется для запланированных действий и намерений в будущем.

Формула: **am/is/are + going to + глагол**.

- *I **am going to** study tonight.*
- *She **is going to** buy a new car.*
- *They **are going to** travel next summer.*

Отрицание: *I **am not going to** wait.* Вопрос: *Are you going to come?*

Отличие от **will**: **going to** — это уже принятое решение или очевидный план, а **will** — решение в момент речи.""",
    ),
]


def seed_rules(apps, schema_editor):
    Language = apps.get_model('core', 'Language')
    GrammarRule = apps.get_model('grammar', 'GrammarRule')

    english = Language.objects.get(code='en')
    for level, order, title, body in RULES:
        GrammarRule.objects.get_or_create(
            language=english,
            title=title,
            defaults={'level': level, 'order': order, 'body': body},
        )


def remove_rules(apps, schema_editor):
    GrammarRule = apps.get_model('grammar', 'GrammarRule')
    GrammarRule.objects.filter(language__code='en', title__in=[r[2] for r in RULES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('grammar', '0004_grammarprogress'),
    ]

    operations = [
        migrations.RunPython(seed_rules, remove_rules),
    ]
