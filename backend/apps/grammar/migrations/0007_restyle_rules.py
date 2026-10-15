"""Rewrite the seeded rules with formula / example / note blocks (see apps/web/rule_render.py)."""
from django.db import migrations

LEGEND = """```legend
s: подлежащее
v: глагол / сказуемое
o: дополнение / то, чем является
m: время, место, уточнение
```"""

EN = {
    'Глагол to be (am/is/are)': LEGEND + """

Глагол **to be** («быть») нужен, когда сказуемое — не действие, а состояние: кто-то *является* кем-то, *находится* где-то, *обладает* качеством. В русском «быть» в настоящем времени пропадает («Я студент»), а в английском его выбросить нельзя.

## Формы

| Лицо | Форма | Сокращение | Пример |
|---|---|---|---|
| I | **am** | I'm | I am a developer. |
| he / she / it | **is** | he's / she's / it's | She is at work. |
| we / you / they | **are** | we're / you're / they're | They are ready. |

## Формулы

```formula
+ | [s: Subject] + [v: am/is/are] + [o: Complement]
− | [s: Subject] + [v: am/is/are + not] + [o: Complement]
? | [v: Am/Is/Are] + [s: Subject] + [o: Complement] [f: ?]
```

```example
[s: She] [v: is] [o: a student]
= Она студентка.
```

```example
[s: They] [v: aren't] [o: ready]
= Они не готовы.
```

```example
[v: Is] [s: he] [o: in the office] ? — Yes, he is.
= Он в офисе? — Да.
```

## Что стоит после to be

```pills
a teacher — кто
tired — какой
in Bishkek — где
25 years old — возраст
from Osh — откуда
```

```note
! | **I amn't** не существует — только `I'm not`. В коротком ответе «да» не сокращают: `Yes, I am`, но не `Yes, I'm`.
```

```note
× | `I am work`, `She is like coffee` — ошибка: to be не ставится перед обычным глаголом-действием. Правильно: `I work`, `She likes coffee`.
```""",

    'Артикли a / an / the': """Артикль — маленькое слово перед существительным, которого нет в русском. Он показывает, *какой именно* предмет имеется в виду.

## a / an — «какой-то, один из»

```formula
[m: a] + [o: согласный звук]  ·  [m: an] + [o: гласный звук]
```

```example
[m: a] [o: dog] , [m: a] [o: book] , [m: a] [o: university]
= собака, книга, университет (u звучит как «ю» — согласный звук)
```

```example
[m: an] [o: apple] , [m: an] [o: hour]
= яблоко, час (h не читается — гласный звук)
```

## the — «тот самый»

```example
[s: I] [v: have] [m: a] [o: cat] . [m: The] [s: cat] [v: is] [o: black]
= У меня есть кот. Этот кот чёрный. (мы уже знаем, о каком коте речь)
```

```cards
Впервые / один из | a / an | какой-то | a cat, an idea
Уже известно | the | тот самый | the cat, the sun
```

## Без артикля

```pills
music — неисчисляемое «вообще»
cats — мн. число «вообще»
Aziz — имена
France — большинство стран
```

```note
! | Выбор a или an зависит от **звука**, а не от буквы: `an hour`, но `a university`.
```""",

    'Present Simple — настоящее простое': LEGEND + """

Факты, привычки, расписания — то, что происходит регулярно или всегда верно.

## Формулы

```formula
+ | [s: I / You / We / They] + [v: V] + [o: Object]
+ | [s: He / She / It] + [v: V + s/es] + [o: Object]
− | [s: Subject] + [f: don't/doesn't] + [v: V] + [o: Object]
? | [f: Do/Does] + [s: Subject] + [v: V] + [o: Object] [f: ?]
```

```example
[s: She] [v: works] [m: every day]
= Она работает каждый день.
```

```example
[s: He] [f: doesn't] [v: drink] [o: coffee]
= Он не пьёт кофе.
```

```example
[f: Do] [s: they] [v: work] [m: on weekends] ?
= Они работают по выходным?
```

## Окончание -s / -es

| Глагол | he / she / it |
|---|---|
| work | work**s** |
| go, watch, fix | go**es**, watch**es**, fix**es** |
| study (согласная + y) | stud**ies** |
| have | **has** |

```pills
always — всегда
usually — обычно
often — часто
every day — каждый день
```

```note
× | После `doesn't` окончание -s пропадает: `He doesn't works` — ошибка, правильно `He doesn't work`.
```""",

    'Личные местоимения': """Местоимение-подлежащее в английском обязательно — даже там, где по-русски его опускают («Иду домой» → *I am going home*).

| Местоимение | Перевод | to be | Пример |
|---|---|---|---|
| I | я | **am** | I am here. |
| you | ты / вы | **are** | You are right. |
| he | он | **is** | He is busy. |
| she | она | **is** | She is a doctor. |
| it | оно (предмет, животное) | **is** | It is cold. |
| we | мы | **are** | We are late. |
| they | они | **are** | They are friends. |

```example
[s: It] [v: is] [o: cold] [m: today]
= Сегодня холодно. (подлежащее it обязательно)
```

```note
! | **you** — и «ты», и «вы»: отдельной вежливой формы нет. **I** всегда пишется с большой буквы.
```""",

    'Множественное число существительных': """## Правила

```formula
обычно | [o: noun] + [m: s]
-s, -sh, -ch, -x, -o | [o: noun] + [m: es]
согласная + y | [o: city] → [o: cit] + [m: ies]
```

| Правило | Пример |
|---|---|
| + **-s** | cat → cat**s**, book → book**s** |
| + **-es** | bus → bus**es**, box → box**es**, watch → watch**es** |
| y → **ies** | city → cit**ies**, baby → bab**ies** |
| гласная + y → **+s** | day → day**s**, boy → boy**s** |

## Исключения

```pills
man → men — мужчины
woman → women — женщины
child → children — дети
foot → feet — ступни
tooth → teeth — зубы
person → people — люди
```

```note
! | После мн. числа глагол тоже меняется: `The cat is` → `The cats are`.
```""",

    'Указательные местоимения this/that/these/those': LEGEND + """

Выбор зависит от двух вещей: **близко или далеко** и **один или много**.

```cards
Близко · один | this | этот, эта, это | this book, this laptop
Близко · много | these | эти | these books, these files
Далеко · один | that | тот, та, то | that house, that server
Далеко · много | those | те | those people, those days
```

## Перед существительным

```formula
[m: this/that/these/those] + [s: noun] + [v: is/are] + [o: Complement]
```

```example
[m: This] [s: laptop] [v: is] [o: new]
= Этот ноутбук новый.
```

## Вместо существительного

```formula
+ | [m: This/That] + [v: is] + [o: a/an + noun]
+ | [m: These/Those] + [v: are] + [o: nouns]
? | [v: Is] + [m: this/that] + [o: …] [f: ?] → [f: Yes, it is.]
```

```example
[m: This] [v: is] [o: my colleague, Aziz]
= Это мой коллега, Азиз. (так представляют людей)
```

```example
[m: These] [v: are] [o: my books]
= Это мои книги. (множественное — these, не this)
```

```note
это ≠ this | Про уже сказанное «это» — `that` или `it`: «Это интересно» → `That's interesting`.
```""",

    'Вопросительные слова': LEGEND + """

Вопросительное слово всегда встаёт в самое начало, перед вспомогательным глаголом.

```pills
What — что
Where — где
Who — кто
When — когда
Why — почему
How — как
```

## Формулы

```formula
to be | [m: Wh-word] + [v: am/is/are] + [s: Subject] [f: ?]
глагол | [m: Wh-word] + [f: do/does/did] + [s: Subject] + [v: V] [f: ?]
```

```example
[m: What] [v: is] [s: your name] ?
= Как тебя зовут?
```

```example
[m: Where] [f: do] [s: you] [v: live] ?
= Где ты живёшь?
```

```example
[m: Why] [f: did] [s: the build] [v: fail] ?
= Почему сборка упала?
```

```note
× | `Where you live?` — ошибка: без `do/does/did` вопрос не строится. Правильно: `Where do you live?`
```""",

    'Present Continuous — настоящее длительное': LEGEND + """

Действие происходит в момент речи или в текущий период («сейчас», «в эти дни»).

## Формулы

```formula
+ | [s: Subject] + [f: am/is/are] + [v: V-ing] + [o: Object]
− | [s: Subject] + [f: am/is/are + not] + [v: V-ing]
? | [f: Am/Is/Are] + [s: Subject] + [v: V-ing] [f: ?]
```

```example
[s: I] [f: am] [v: fixing] [o: a bug] [m: right now]
= Я сейчас чиню баг.
```

```example
[s: She] [f: isn't] [v: working] [m: today]
= Она сегодня не работает.
```

```example
[f: Are] [s: you] [v: watching] [o: TV] ?
= Ты смотришь телевизор?
```

```pills
now — сейчас
right now — прямо сейчас
at the moment — в данный момент
Look! — Смотри!
```

```note
vs. Simple | `I work` — работаю вообще (профессия, привычка). `I am working` — работаю прямо сейчас.
```

```note
× | `I working` — без am/is/are нельзя. `I am know` — know, like, want обычно не ставят в -ing: `I know`.
```""",

    'Past Simple — прошедшее простое (правильные глаголы)': LEGEND + """

Действие произошло и закончилось в прошлом, обычно с указанием времени.

## Формулы

```formula
+ | [s: Subject] + [v: V-ed] + [o: Object] + [m: Time]
− | [s: Subject] + [f: didn't] + [v: V] + [o: Object]
? | [f: Did] + [s: Subject] + [v: V] + [o: Object] [f: ?]
```

```example
[s: We] [v: launched] [o: the project] [m: last month]
= Мы запустили проект в прошлом месяце.
```

```example
[s: I] [f: didn't] [v: work] [m: yesterday]
= Я не работал вчера.
```

```example
[f: Did] [s: you] [v: call] [o: him] ?
= Ты ему звонил?
```

| Правило | Пример |
|---|---|
| + **-ed** | work → work**ed** |
| на -e → **+d** | live → live**d** |
| согласная + y → **ied** | study → stud**ied** |
| короткий слог → удвоение | stop → sto**pped** |

```pills
yesterday — вчера
last week — на прошлой неделе
in 2020 — в 2020 году
two days ago — два дня назад
```

```note
× | После `did` глагол в базовой форме: `Did you worked?` — ошибка, правильно `Did you work?`
```""",

    'There is / There are': LEGEND + """

Когда говорим, что что-то *есть* или *находится* где-то, и это новая информация. Русский начинает с места («В комнате есть стол»), английский — с **there**.

## Формулы

```formula
+ | [f: There] + [v: is/are] + [o: что] + [m: где]
− | [f: There] + [v: isn't/aren't] + [o: any / a] + [m: где]
? | [v: Is/Are] + [f: there] + [o: что] + [m: где] [f: ?]
```

```example
[f: There] [v: is] [o: a book] [m: on the table]
= На столе книга.
```

```example
[f: There] [v: are] [o: two cats] [m: in the garden]
= В саду две кошки.
```

```example
[v: Is] [f: there] [o: a shop] [m: nearby] ? — Yes, there is.
= Рядом есть магазин? — Да.
```

## По временам

| Время | Ед. число | Мн. число |
|---|---|---|
| Present | **there is** | **there are** |
| Past | **there was** | **there were** |
| Future | **there will be** | **there will be** |

```note
! | Глагол согласуется с первым существительным: `There is a pen and two books`.
```""",

    'Предлоги места in, on, at': LEGEND + """

Три самых частых предлога места.

```cards
Внутри | in | в | in the room, in London
На поверхности | on | на | on the table, on the wall
У точки | at | у, в, на | at the door, at school
```

```formula
[s: Subject] + [v: is/are] + [m: in/on/at] + [o: place]
```

```example
[s: She] [v: is] [m: at] [o: school]
= Она в школе. (как в месте, где учатся)
```

```example
[s: The keys] [v: are] [m: on] [o: the table]
= Ключи на столе.
```

```example
[s: I] [v: live] [m: in] [o: Bishkek]
= Я живу в Бишкеке.
```

```note
! | «В» не всегда `in`: `at work`, `at home`, `at the bus stop`; а «на» не всегда `on`: `in the street` (брит.), `at the concert`.
```""",

    'Some / any': LEGEND + """

**some** и **any** — «несколько, немного». Работают с исчисляемыми во мн. числе (*apples*) и неисчисляемыми (*water*).

```formula
+ | [s: Subject] + [v: Verb] + [m: some] + [o: noun]
− | [s: Subject] + [f: don't] + [v: Verb] + [m: any] + [o: noun]
? | [f: Do] + [s: Subject] + [v: Verb] + [m: any] + [o: noun] [f: ?]
```

```example
[s: I] [v: have] [m: some] [o: apples]
= У меня есть несколько яблок.
```

```example
[s: I] [f: don't] [v: have] [m: any] [o: water]
= У меня совсем нет воды.
```

```example
[f: Do] [s: you] [v: have] [m: any] [o: questions] ?
= У вас есть вопросы?
```

```note
! | В просьбах и предложениях — **some**, даже в вопросе: `Would you like some tea?`, `Can I have some water?`
```""",

    'Сравнительная и превосходная степень прилагательных': LEGEND + """

Сравнить два предмета — сравнительная степень, выделить один из многих — превосходная.

## Формулы

```formula
сравн. | [s: A] + [v: is] + [o: adj-er / more adj] + [m: than] + [o: B]
превосх. | [s: A] + [v: is] + [m: the] + [o: adj-est / most adj]
```

| Тип | Сравнительная | Превосходная |
|---|---|---|
| короткие | tall → **taller** | **the tallest** |
| удвоение | big → **bigger** | **the biggest** |
| на -y | easy → **easier** | **the easiest** |
| длинные | interesting → **more interesting** | **the most interesting** |
| good | **better** | **the best** |
| bad | **worse** | **the worst** |

```example
[s: This book] [v: is] [o: more interesting] [m: than] [o: that one]
= Эта книга интереснее той.
```

```example
[s: Everest] [v: is] [m: the] [o: highest mountain] [m: in the world]
= Эверест — самая высокая гора в мире.
```

```note
× | `more better`, `the most biggest` — двойное сравнение не используют.
```""",

    'Модальный глагол can': LEGEND + """

**can** — умение, возможность, разрешение. После модальных глаголов смысловой глагол всегда в базовой форме: без **to** и без **-s**.

```formula
+ | [s: Subject] + [f: can] + [v: V] + [o: Object]
− | [s: Subject] + [f: can't] + [v: V]
? | [f: Can] + [s: Subject] + [v: V] [f: ?]
```

```example
[s: She] [f: can] [v: speak] [o: three languages]
= Она говорит на трёх языках.
```

```example
[s: I] [f: can't] [v: drive]
= Я не умею водить.
```

```example
[f: Can] [s: you] [v: help] [o: me] ?
= Можешь мне помочь?
```

| Смысл | Пример |
|---|---|
| умение | I **can** swim. |
| разрешение | You **can** go now. |
| просьба | **Can** you open the door? |

```note
× | `she cans speak`, `she can to speak` — ошибки: после can нет ни -s, ни to.
```""",

    'Оборот going to (будущее время)': LEGEND + """

**be going to** — для планов и намерений, о которых уже решено.

```formula
+ | [s: Subject] + [f: am/is/are going to] + [v: V] + [o: Object]
− | [s: Subject] + [f: am/is/are not going to] + [v: V]
? | [f: Am/Is/Are] + [s: Subject] + [f: going to] + [v: V] [f: ?]
```

```example
[s: I] [f: am going to] [v: study] [m: tonight]
= Я собираюсь заниматься вечером.
```

```example
[s: We] [f: are going to] [v: release] [o: version 2.0] [m: next week]
= Мы выпустим версию 2.0 на следующей неделе.
```

```example
[f: Are] [s: you] [f: going to] [v: come] ?
= Ты придёшь?
```

```cards
Уже решено, план | going to | собираюсь | I'm going to buy a car.
Решение сейчас | will | сделаю | OK, I'll help you.
```

```note
× | `I going to`, `I am going to buying` — нужно и `am/is/are`, и базовая форма глагола.
```""",
}

DE = {
    'Глагол sein (быть)': LEGEND + """

**sein** — самый частый глагол в немецком, и он неправильный: формы нужно запомнить.

| Кто | Форма | Пример |
|---|---|---|
| ich | **bin** | Ich bin Student. |
| du | **bist** | Du bist müde. |
| er / sie / es | **ist** | Sie ist glücklich. |
| wir | **sind** | Wir sind Freunde. |
| ihr | **seid** | Ihr seid spät dran. |
| sie / Sie | **sind** | Sie sind aus Deutschland. |

## Формулы

```formula
+ | [s: Subjekt] + [v: sein] + [o: Ergänzung]
− | [s: Subjekt] + [v: sein] + [m: nicht] + [o: Ergänzung]
? | [v: sein] + [s: Subjekt] + [o: Ergänzung] [f: ?]
```

```example
[s: Ich] [v: bin] [o: Student]
= Я студент.
```

```example
[s: Ich] [v: bin] [m: nicht] [o: müde]
= Я не устал.
```

```example
[v: Bist] [s: du] [o: zu Hause] ?
= Ты дома?
```

```note
! | Перед профессией артикль не нужен: `Ich bin Lehrer`, а не `Ich bin ein Lehrer`.
```""",

    'Артикли der/die/das': """У каждого существительного есть род, и артикль зависит от него.

```cards
Мужской | der | ein | der Mann
Женский | die | eine | die Frau
Средний | das | ein | das Kind
Множественное | die | — | die Kinder
```

```example
[m: Der] [s: Mann] [v: ist] [o: groß]
= Мужчина высокий.
```

```example
[s: Ich] [v: habe] [m: eine] [o: Katze]
= У меня есть кошка.
```

```note
! | Род почти никогда нельзя угадать по смыслу — учите слово вместе с артиклем: не «Wasser», а **das Wasser**.
```

```note
подсказка | -ung, -heit, -keit → **die**; -chen, -lein → **das**; дни недели и месяцы → **der**.
```""",

    'Настоящее время (Präsens)': LEGEND + """

Глагол меняет окончание по лицам. Образец — **machen** (делать):

| Кто | Окончание | Пример |
|---|---|---|
| ich | **-e** | ich mach**e** |
| du | **-st** | du mach**st** |
| er / sie / es | **-t** | er mach**t** |
| wir | **-en** | wir mach**en** |
| ihr | **-t** | ihr mach**t** |
| sie / Sie | **-en** | sie mach**en** |

## Формулы

```formula
+ | [s: Subjekt] + [v: Verb] + [o: Objekt]
− | [s: Subjekt] + [v: Verb] + [o: Objekt] + [m: nicht]
? | [v: Verb] + [s: Subjekt] + [o: Objekt] [f: ?]
```

```example
[s: Ich] [v: mache] [o: das] [m: nicht]
= Я этого не делаю.
```

```example
[v: Machst] [s: du] [o: das] ?
= Ты это делаешь?
```

```note
! | Одна форма Präsens = и «делаю», и «сейчас делаю», и часто «сделаю»: `Morgen mache ich das`.
```""",

    'Личные местоимения': """| Местоимение | Перевод |
|---|---|
| ich | я |
| du | ты |
| er / sie / es | он / она / оно |
| wir | мы |
| ihr | вы (несколько человек, неформально) |
| sie | они |
| Sie | Вы (вежливая форма) |

```example
[s: Sie] [v: sind] [o: sehr nett]
= Вы очень любезны. (вежливое Sie — с большой буквы)
```

```example
[s: Ihr] [v: seid] [o: hier]
= Вы (ребята) здесь.
```

```note
! | **Sie** с большой буквы — вежливое «Вы» к одному или нескольким людям. Используйте его с незнакомыми и в официальной обстановке.
```""",

    'Множественное число существительных': """Единого правила нет — форму мн. числа учат вместе со словом. Основные типы:

| Тип | Пример |
|---|---|
| **-e** | der Hund → die Hund**e** |
| **-er** (+ умлаут) | das Buch → die Büch**er** |
| **-(e)n** | die Frau → die Frau**en** |
| **-s** (заимствования) | das Auto → die Auto**s** |
| без окончания (+ умлаут) | der Vater → die V**ä**ter |

```example
[m: Die] [s: Kinder] [v: spielen]
= Дети играют.
```

```note
! | Во мн. числе артикль всегда **die**, независимо от рода в единственном.
```""",

    'Указательные местоимения dieser/diese/dieses': """«Этот / эта / это» согласуется с родом существительного — окончание как у артикля.

```cards
Мужской | dieser | der → dieser | dieser Mann
Женский | diese | die → diese | diese Frau
Средний | dieses | das → dieses | dieses Kind
Множественное | diese | die → diese | diese Kinder
```

```formula
[m: dieser/diese/dieses] + [s: Nomen] + [v: Verb] + [o: …]
```

```example
[m: Dieses] [s: Buch] [v: ist] [o: interessant]
= Эта книга интересная.
```

```note
! | dies + окончание артикля: der → dies**er**, die → dies**e**, das → dies**es**.
```""",

    'Вопросительные слова': LEGEND + """

Вопросительное слово — на первом месте, глагол — сразу за ним.

```pills
was — что
wo — где
wer — кто
wann — когда
warum — почему
wie — как
```

```formula
[m: W-Wort] + [v: Verb] + [s: Subjekt] + [o: …] [f: ?]
```

```example
[m: Wie] [v: heißt] [s: du] ?
= Как тебя зовут?
```

```example
[m: Wo] [v: wohnst] [s: du] ?
= Где ты живёшь?
```

```note
× | `Wo du wohnst?` — ошибка: глагол должен стоять сразу после вопросительного слова.
```""",

    'Perfekt — разговорное прошедшее время': LEGEND + """

В устной речи немцы почти всегда говорят о прошлом через **Perfekt**.

```formula
[s: Subjekt] + [f: haben/sein] + [o: …] + [v: Partizip II]
```

```example
[s: Ich] [f: habe] [o: ein Buch] [v: gelesen]
= Я прочитал книгу.
```

```example
[s: Er] [f: ist] [m: nach Berlin] [v: gefahren]
= Он поехал в Берлин.
```

```cards
Движение, смена состояния | sein | gehen, fahren, kommen | Ich bin gekommen.
Всё остальное | haben | machen, lesen, essen | Ich habe gegessen.
```

```formula
Partizip II | [m: ge] + [v: основа] + [m: t] → [v: gemacht]
```

```note
! | Partizip II всегда уходит **в конец** предложения.
```""",

    'Порядок слов: глагол на втором месте': LEGEND + """

Спрягаемый глагол в утвердительном предложении всегда стоит **на втором месте** — неважно, что на первом.

```formula
обычно | [s: Subjekt] + [v: Verb] + [m: Zeit] + [o: Objekt]
инверсия | [m: Zeit / Ort] + [v: Verb] + [s: Subjekt] + [o: Objekt]
```

```example
[s: Ich] [v: lese] [m: heute] [o: ein Buch]
= Я сегодня читаю книгу.
```

```example
[m: Heute] [v: lese] [s: ich] [o: ein Buch]
= Сегодня я читаю книгу. (ich уходит после глагола)
```

```note
× | `Heute ich lese ein Buch` — ошибка. Глагол второй — железное правило.
```""",
}


def restyle(apps, schema_editor):
    GrammarRule = apps.get_model('grammar', 'GrammarRule')
    for code, rules in (('en', EN), ('de', DE)):
        for title, body in rules.items():
            GrammarRule.objects.filter(language__code=code, title=title).update(body=body.strip())


class Migration(migrations.Migration):

    dependencies = [
        ('grammar', '0006_alter_grammarrule_body'),
    ]

    operations = [
        migrations.RunPython(restyle, migrations.RunPython.noop),
    ]
