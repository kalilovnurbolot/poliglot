from django.db import migrations

RULES = [
    (
        'A1', 1, 'Глагол to be (am/is/are)',
        """Глагол **to be** ("быть") — самый частый глагол в английском. В настоящем времени у него три формы:

| Кто | Форма | Пример |
|---|---|---|
| I | am | I **am** a student. |
| he/she/it | is | She **is** happy. |
| we/you/they | are | They **are** friends. |

Отрицание — просто добавь **not**: *I am not (I'm not) tired.*

Вопрос — переставь местами: *Is she happy? Are they friends?*""",
    ),
    (
        'A1', 2, 'Артикли a / an / the',
        """**a** и **an** — неопределённые артикли, ставятся перед исчисляемым существительным в единственном числе, когда речь о чём-то одном из многих:
- **a** dog, **a** book — перед согласным звуком
- **an** apple, **an** hour — перед гласным звуком

**the** — определённый артикль, используется, когда понятно, о каком именно предмете речь:
- *I have a cat. **The** cat is black.* (мы уже знаем, о каком коте речь)

Перед именами, странами (кроме нескольких исключений) и неисчисляемыми существительными "вообще" артикль обычно не нужен: *I like music. She lives in France.*""",
    ),
    (
        'A1', 3, 'Present Simple — настоящее простое',
        """Используется для привычных действий, фактов и расписаний.

Утверждение: *I/you/we/they **work**.* В 3-м лице единственного числа (he/she/it) добавляется **-s**: *She **works**.*

Отрицание: **don't/doesn't** + глагол без -s: *I **don't** work. He **doesn't** work.*

Вопрос: **Do/Does** + подлежащее + глагол: *Do you work? Does she work?*

Слова-маркеры: usually, often, always, every day.""",
    ),
    (
        'A1', 4, 'Личные местоимения',
        """| Местоимение | Перевод |
|---|---|
| I | я |
| you | ты / вы |
| he / she / it | он / она / оно |
| we | мы |
| they | они |

В английском **you** используется и для "ты", и для "вы" — отдельной вежливой формы нет.""",
    ),
    (
        'A1', 5, 'Множественное число существительных',
        """Обычно просто добавляем **-s**: *cat → cats, book → books*.

После шипящих (-s, -sh, -ch, -x, -o) добавляем **-es**: *bus → buses, box → boxes*.

Если слово оканчивается на согласную + **-y**, меняем **y на i** и добавляем **-es**: *city → cities*.

Есть и исключения, которые нужно просто запомнить: *man → men, child → children, foot → feet*.""",
    ),
    (
        'A1', 6, 'Указательные местоимения this/that/these/those',
        """- **this** (этот/эта/это) — для одного предмета рядом: *this book*
- **these** (эти) — для нескольких предметов рядом: *these books*
- **that** (тот/та/то) — для одного предмета вдалеке: *that house*
- **those** (те) — для нескольких предметов вдалеке: *those houses*

Короче: this/these — "близко", that/those — "далеко".""",
    ),
    (
        'A1', 7, 'Вопросительные слова',
        """| Слово | Значение |
|---|---|
| what | что |
| where | где |
| who | кто |
| when | когда |
| why | почему |
| how | как |

Пример: *What is your name? Where do you live?*""",
    ),
    (
        'A2', 1, 'Present Continuous — настоящее длительное',
        """Используется для действий, происходящих прямо сейчас, или временных ситуаций.

Формула: **am/is/are + глагол-ing**.
- *I **am reading** a book right now.*
- *She **is working** today.*
- *They **are watching** TV.*

Слова-маркеры: now, right now, at the moment, look!, listen!""",
    ),
    (
        'A2', 2, 'Past Simple — прошедшее простое (правильные глаголы)',
        """Для правильных глаголов добавляем **-ed**: *work → work**ed**, play → play**ed**.*

Отрицание и вопрос строятся с **did**: *I **didn't** work yesterday. **Did** you work yesterday?*
В отрицании и вопросе глагол возвращается в начальную форму без -ed.

Слова-маркеры: yesterday, last week, in 2020, ago.""",
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
        ('grammar', '0001_initial'),
        ('core', '0002_seed_english_language'),
    ]

    operations = [
        migrations.RunPython(seed_rules, remove_rules),
    ]
