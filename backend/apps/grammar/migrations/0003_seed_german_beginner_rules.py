from django.db import migrations

RULES = [
    (
        'A1', 1, 'Глагол sein (быть)',
        """Глагол **sein** ("быть") — самый частый глагол в немецком, и он неправильный, его формы нужно просто запомнить:

| Кто | Форма | Пример |
|---|---|---|
| ich | bin | Ich **bin** Student. |
| du | bist | Du **bist** müde. |
| er/sie/es | ist | Sie **ist** glücklich. |
| wir | sind | Wir **sind** Freunde. |
| ihr | seid | Ihr **seid** spät dran. |
| sie/Sie | sind | Sie **sind** aus Deutschland. |

Отрицание — добавь **nicht**: *Ich bin **nicht** müde.*""",
    ),
    (
        'A1', 2, 'Артикли der/die/das',
        """В немецком у каждого существительного есть род, и артикль зависит от него:
- **der** — мужской род: *der Mann* (мужчина)
- **die** — женский род: *die Frau* (женщина)
- **das** — средний род: *das Kind* (ребёнок)
- **die** — множественное число для любого рода: *die Kinder*

Неопределённые артикли ("один из многих"): **ein** (муж./ср. род), **eine** (жен. род) — *ein Mann, eine Frau, ein Kind*.

Род существительного почти никогда нельзя угадать по смыслу слова — его нужно запоминать вместе со словом: не "Wasser", а "**das** Wasser".""",
    ),
    (
        'A1', 3, 'Настоящее время (Präsens)',
        """Немецкие глаголы в настоящем времени спрягаются по лицам. Окончания для правильных глаголов (на примере **machen** — делать):

| Кто | Окончание | Пример |
|---|---|---|
| ich | -e | ich mach**e** |
| du | -st | du mach**st** |
| er/sie/es | -t | er mach**t** |
| wir | -en | wir mach**en** |
| ihr | -t | ihr mach**t** |
| sie/Sie | -en | sie mach**en** |

Отрицание строится с **nicht**: *Ich mache das nicht.* Вопрос — глагол выходит на первое место: *Machst du das?*""",
    ),
    (
        'A1', 4, 'Личные местоимения',
        """| Местоимение | Перевод |
|---|---|
| ich | я |
| du | ты |
| er / sie / es | он / она / оно |
| wir | мы |
| ihr | вы (несколько человек, неформально) |
| sie | они |
| Sie | Вы (вежливая форма, с большой буквы) |

В отличие от английского, в немецком есть отдельная вежливая форма **Sie** — используется с незнакомыми людьми и в официальной обстановке.""",
    ),
    (
        'A1', 5, 'Множественное число существительных',
        """В немецком нет единого правила — окончание множественного числа нужно запоминать вместе со словом. Основные типы:
- **-e**: der Hund → die Hund**e** (собаки)
- **-er** (часто + умлаут): das Buch → die Büch**er** (книги)
- **-(e)n**: die Frau → die Frau**en** (женщины)
- **-s** (часто у заимствований): das Auto → die Auto**s** (машины)
- без окончания (часто + умлаут): der Vater → die Väter (отцы)

Во множественном числе артикль всегда **die**, независимо от рода в единственном числе.""",
    ),
    (
        'A1', 6, 'Указательные местоимения dieser/diese/dieses',
        """"Этот/эта/это" в немецком согласуется с родом существительного:
- **dieser** — мужской род: *dieser Mann* (этот мужчина)
- **diese** — женский род: *diese Frau* (эта женщина)
- **dieses** — средний род: *dieses Kind* (этот ребёнок)
- **diese** — множественное число: *diese Kinder* (эти дети)

Запомнить проще всего по аналогии с артиклем: dies + окончание артикля (der→dieser, die→diese, das→dieses).""",
    ),
    (
        'A1', 7, 'Вопросительные слова',
        """| Слово | Значение |
|---|---|
| was | что |
| wo | где |
| wer | кто |
| wann | когда |
| warum | почему |
| wie | как |

Пример: *Wie heißt du? Wo wohnst du?* — вопросительное слово всегда стоит на первом месте, а глагол — сразу после него.""",
    ),
    (
        'A2', 1, 'Perfekt — разговорное прошедшее время',
        """В устной речи немцы почти всегда используют **Perfekt**, а не простое прошедшее.

Формула: **haben/sein + Partizip II** (причастие прошедшего времени), которое уходит в конец предложения.

- *Ich **habe** ein Buch **gelesen**.* (Я прочитал книгу.)
- *Er **ist** nach Berlin **gefahren**.* (Он поехал в Берлин.)

**sein** используют глаголы движения/изменения состояния (gehen, fahren, kommen), для остальных — **haben**.

Partizip II для правильных глаголов: **ge- + основа + -t** (machen → ge**mach**t).""",
    ),
    (
        'A2', 2, 'Порядок слов: глагол на втором месте',
        """Главное правило немецкого порядка слов: спрягаемый глагол всегда стоит **на втором месте** в утвердительном предложении — неважно, что стоит на первом.

- *Ich lese heute ein Buch.* (Я)
- *Heute lese ich ein Buch.* (Сегодня — глагол всё равно второй, а "ich" уходит после него!)

Это отличается от английского и русского, где порядок слов свободнее. Второе место глагола — железное правило, к которому важно привыкнуть с самого начала.""",
    ),
]


def seed_rules(apps, schema_editor):
    Language = apps.get_model('core', 'Language')
    GrammarRule = apps.get_model('grammar', 'GrammarRule')

    german = Language.objects.get(code='de')
    for level, order, title, body in RULES:
        GrammarRule.objects.get_or_create(
            language=german,
            title=title,
            defaults={'level': level, 'order': order, 'body': body},
        )


def remove_rules(apps, schema_editor):
    GrammarRule = apps.get_model('grammar', 'GrammarRule')
    GrammarRule.objects.filter(language__code='de', title__in=[r[2] for r in RULES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('grammar', '0002_seed_beginner_rules'),
        ('core', '0003_seed_german_language'),
    ]

    operations = [
        migrations.RunPython(seed_rules, remove_rules),
    ]
