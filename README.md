# Полиглот

Приложение для изучения языков: заучивание слов свайпами, грамматика для начинающих, квизы (в т.ч. на слух). MVP — только английский язык.

## Стек
- **backend/** — Django + Django REST Framework (API)
- **frontend/** — Next.js (App Router, TypeScript, Tailwind)

## Запуск (локально, sqlite, без Docker)

Backend:
```bash
cd backend
source .venv/bin/activate
python manage.py migrate
python manage.py runserver 8000
```

Frontend:
```bash
cd frontend
npm run dev
```

Фронтенд ждёт бэкенд на `http://localhost:8000/api` (см. `frontend/.env.local`). Проверка связи — `http://localhost:3000`, должно быть "Backend: ✅ подключен".

## Запуск с Postgres (без остального Docker)

```bash
docker-compose up -d db
```

Затем в `backend/.env` раскомментировать `DATABASE_URL` и выполнить `python manage.py migrate`.

## Локальный деплой (Docker Compose, production-режим)

Полный стек — Postgres + Django/gunicorn + Next.js production-сборка — одной командой:

```bash
cp .env.example .env                              # GOOGLE_OAUTH_CLIENT_ID для сборки фронтенда
cp backend/.env.docker.example backend/.env.docker # SECRET_KEY, GOOGLE_OAUTH_CLIENT_ID для бэкенда
docker compose up --build -d
```

- Фронтенд: http://localhost:3000
- Бэкенд/админка: http://localhost:8000 (admin, api)

При старте контейнер бэкенда сам накатывает миграции и собирает статику (`entrypoint.sh`). `NEXT_PUBLIC_*` переменные для фронтенда — build-time (Next.js инлайнит их при сборке), поэтому передаются как build args в `docker-compose.yml`, а не через обычный env файл контейнера.

Управление:
```bash
docker compose logs -f          # логи всех сервисов
docker compose down             # остановить (данные Postgres сохранятся в volume)
docker compose down -v          # остановить и стереть данные Postgres
docker compose up --build -d    # пересобрать после изменений в коде
```

Создать себе админа внутри контейнера:
```bash
docker compose exec backend python manage.py createsuperuser
```

Отличия от обычного `npm run dev`/`runserver` для разработки:
- `DEBUG=False`, статика Django раздаётся через `whitenoise` вместо `runserver`
- Next.js собран в `output: "standalone"` и запускается через `next start` (`node server.js`), а не dev-сервер с hot reload
- Postgres вместо sqlite

Это локальный прод-деплой (на вашей машине) — для реального внешнего хостинга (Vercel/Railway/VPS и т.п.) образы те же самые, но нужно будет: сменить `NEXT_PUBLIC_API_URL`/`CORS_ALLOWED_ORIGINS`/`ALLOWED_HOSTS` на реальный домен, завести отдельный git-репозиторий проекта и добавить домен в Google Cloud Console (Authorized JavaScript origins) для OAuth.

## Структура backend
- `config/` — настройки Django, корневые urls
- `apps/core/` — общие вещи: `Language` (сейчас засеян только `en`/English), health-check `/api/health/`
- `apps/vocabulary/` — `Deck`, `Word`, `UserWordProgress` + SRS-логика (`srs.py`) и API для экрана заучивания
- `apps/grammar/` — `GrammarRule` (грамматические темы по уровням A1–C2)
- `apps/users/` — кастомная модель `User` (логин по email, без username), регистрация/вход, Google OAuth
- `apps/*` — будущие приложения: квизы

## API (фаза 2)
Системные объекты (`owner = null`) видны всем и доступны только на чтение; свои объекты может редактировать только владелец. Запись требует авторизации.

- `GET /api/languages/` — список языков
- `GET/POST /api/decks/` — колоды слов (`?language=en`, `?mine=true`)
- `GET/PUT/PATCH/DELETE /api/decks/{id}/`
- `GET/POST /api/words/` — слова (`?language=en`, `?deck={id}`, `?mine=true`) — так пользователь добавляет свои слова
- `GET/PUT/PATCH/DELETE /api/words/{id}/`
- `GET /api/grammar-rules/` — правила грамматики (`?language=en`, `?level=A1`), только чтение (наполняются через Django Admin)

Для доступа к `/admin/` и авторизованным запросам создайте себе аккаунт:
```bash
python manage.py createsuperuser
```

## Аутентификация (фаза 3)
JWT (access + refresh) через `djangorestframework-simplejwt`. Вход по email/паролю или через Google.

- `POST /api/auth/register/` — `{email, password, first_name}` → создаёт пользователя, возвращает `{user, access, refresh}`
- `POST /api/auth/login/` — `{email, password}` → `{access, refresh}`
- `POST /api/auth/refresh/` — `{refresh}` → новый `access`
- `POST /api/auth/google/` — `{id_token}` (ID-токен от Google Identity Services) → создаёт/находит пользователя по email, возвращает `{user, access, refresh}`
- `GET /api/auth/me/` — текущий пользователь (нужен заголовок `Authorization: Bearer <access>`)

### Google OAuth
Используется схема с ID-токеном (Google Identity Services на фронтенде), поэтому **client secret бэкенду не нужен** — только публичный `client_id`:
- `backend/.env`: `GOOGLE_OAUTH_CLIENT_ID=...` (для проверки токена через `google-auth`)
- `frontend/.env.local`: `NEXT_PUBLIC_GOOGLE_CLIENT_ID=...` (тот же client_id, для рендера кнопки входа)

Файл `client_secret_*.json` из Google Cloud Console в этой схеме не используется и **не должен попадать в git** — секрет из него нигде не хранится в проекте.

Фронтенд: `src/lib/auth-context.tsx` (React-контекст `useAuth()` — `login`, `register`, `loginWithGoogle`, `logout`, `user`), `src/lib/api.ts` (обёртка над `fetch` с авто-обновлением access-токена по refresh-токену), страницы `/login` и `/register`.

## Экран заучивания слов (фаза 4)
SRS по системе Лейтнера (`apps/vocabulary/srs.py`): 8 «коробок» (0–7) с растущими интервалами повтора — от 10 минут до 30 дней.

- `GET /api/review/queue/?language=en&limit=20` — слова к повторению прямо сейчас (`next_review_at <= now`) + новые слова, если очередь не заполнена
- `POST /api/review/answer/` — `{word, direction}`, `direction` ∈ `right|left|up|down`:
  - **right** (знаю) — `box_level += 1`, следующий повтор позже
  - **left** (не знаю) — `box_level = 0`, вернётся через 10 минут
  - **up** (избранное/сложное) — ставит `is_favorite`, не трогает box/счётчики
  - **down** (пропустить) — вообще без эффекта; фронтенд просто откладывает карточку на конец локальной очереди, на бэкенд не отправляется
- `GET /api/review/favorites/` — слова, отмеченные свайпом вверх

Фронтенд — страница `/learn`:
- [FlashCard.tsx](frontend/src/components/FlashCard.tsx) — карточка на `framer-motion` с drag-свайпом в 4 стороны (клик по карточке переворачивает и показывает перевод/пример)
- Дублирующее управление стрелками клавиатуры (←/→/↑/↓) — тот же смысл, что и у свайпов
- Сессионная статистика (знаю/не знаю/избранное) и экран «На сегодня всё» по исчерпании очереди

Стартовый контент — системная колода «Основы» с 18 базовыми словами (засеяна миграцией, `owner=null`, видна всем).

## Раздел «Грамматика» (фаза 5)
`GET /api/grammar-rules/?language=en&level=A1` — уже был реализован в фазе 2, только на чтение, авторизация не нужна. Добавлено в этой фазе:

- Данные: 9 стартовых правил для начинающих (A1: to be, артикли, Present Simple, местоимения, множественное число, this/that, вопросительные слова; A2: Present Continuous, Past Simple) — засеяны миграцией `apps/grammar/migrations/0002_seed_beginner_rules.py`, `body` в Markdown
- Фронтенд `/grammar` — список правил с переключателем уровня (A1–C2)
- `/grammar/[id]` — детальная страница, рендерит `body` через `react-markdown` + `remark-gfm` (таблицы) с типографикой `@tailwindcss/typography`
- Доступно без входа — ссылка «Посмотреть грамматику без регистрации» на главной для неавторизованных

## Квизы (фаза 6)
Новое приложение `apps/quizzes` — без своих моделей, генерирует вопросы на лету из `Word`/`UserWordProgress`.

- `GET /api/quiz/questions/?language=en&limit=10` — список из `{word, options}`: 4 варианта перевода (1 верный + 3 случайных дистрактора), перемешаны. Слова берутся в первую очередь из уже введённых через `/learn` (есть `UserWordProgress`); если introduced-слов меньше 4 — берёт из всего видимого пула, чтобы квиз не был пустым для новых пользователей
- Проверка ответа **не отдельным эндпоинтом** — фронтенд сравнивает выбор с `word.translation` локально и отправляет результат через уже существующий `POST /api/review/answer/` (`right`/`left`), то есть квиз напрямую питает тот же SRS-прогресс, что и свайпы в `/learn` — без дублирования логики/моделей

Фронтенд — страница `/quiz`, два режима переключаются одной кнопкой без запроса новых вопросов:
- **Обычный** — показывает слово текстом, выбираешь перевод
- **На слух** — слово озвучивается через Web Speech API (`speechSynthesis`, `lib/quiz.ts`), текст скрыт до ответа, повторное прослушивание по кнопке 🔊
- Мгновенная подсветка верного/неверного варианта, счётчик сессии, экран результатов с «Пройти ещё раз»

## Добавление своих слов
Backend для этого уже существовал с фазы 2 (`POST /api/words/` сохраняет `owner=request.user`). Добавлен фронтенд:

- `/words` — страница «Мои слова»: форма добавления (слово, перевод, транскрипция и пример — необязательны, часть речи — выбор) и список уже добавленных с удалением
- [lib/words.ts](frontend/src/lib/words.ts) — `fetchLanguages` (чтобы получить id языка `en` для отправки в `POST /api/words/`, так как `language` на бэке — FK по id, а не по коду), `fetchMyWords`, `createWord`, `deleteWord`
- Добавленное слово сразу доступно в `/learn` и `/quiz` — специальной интеграции не потребовалось, оба экрана и так берут слова через `visible_words()` (система + свои)

Заодно исправлен баг, всплывший при тестировании: `POST /api/auth/refresh/` падал с 500 (`User.DoesNotExist`), если refresh-токен ссылался на уже удалённого пользователя (например, после чистки тестовых аккаунтов) — теперь корректный 401. См. `apps/users/views.py: TokenRefreshView`.

## Второй язык: немецкий
Модель данных изначально мультиязычная (`Language`/`Word`/`Deck`/`GrammarRule` — все с FK на `Language`), поэтому добавление языка не потребовало миграции схемы — только данные и переключатель в UI.

**Backend:**
- `apps/core/migrations/0003_seed_german_language.py` — добавляет `Language(code='de', name='Немецкий')`; заодно переименовал `en` в «Английский» для единообразия в русскоязычном UI
- `apps/vocabulary/migrations/0004_seed_basic_german_words.py` — колода «Основы» + 18 базовых немецких слов (те же категории, что у английского списка)
- `apps/grammar/migrations/0003_seed_german_beginner_rules.py` — 9 правил для начинающих: sein, артикли der/die/das, Präsens, местоимения, множественное число, dieser/diese/dieses, вопросительные слова (A1); Perfekt, порядок слов V2 (A2)
- Все существующие эндпоинты (`/api/words/`, `/api/review/*`, `/api/quiz/*`, `/api/grammar-rules/`) уже принимали `?language=<code>` — новых ручек не потребовалось

**Frontend:**
- [lib/language-context.tsx](frontend/src/lib/language-context.tsx) — `LanguageProvider`/`useLanguage()`, список языков из `/api/languages/`, выбранный код хранится в `localStorage` (`poliglot_language`) и переживает перезагрузку
- [components/LanguageSwitcher.tsx](frontend/src/components/LanguageSwitcher.tsx) — выпадающий список, добавлен на главную, `/learn`, `/quiz`, `/grammar`, `/words` (скрывается сам, если язык всего один)
- `/learn`, `/quiz`, `/grammar`, `/words` теперь читают язык из контекста вместо хардкода `"en"` и перезагружают данные при смене языка
- Озвучка в квизе (`speak()` в `lib/quiz.ts`) учитывает язык — `en-US`/`de-DE` для Web Speech API, а не всегда английский

Добавление следующего языка — это только новые data-миграции (Language + слова + правила), без изменений кода.

## Слова по уровню (CEFR)
У `Word` появилось поле `level` (A1–C2) — те же значения, что уже использовались в `GrammarRule`. Enum вынесен в `apps/core/models.py: Level` и теперь переиспользуется обоими приложениями (миграция `grammar` не потребовалась — Django сериализует `choices` как значения, а не ссылку на класс).

**Backend:**
- `apps/vocabulary/migrations/0005_word_level.py` — поле `level`, по умолчанию `A1` (все существующие 36 слов автоматически стали A1)
- `apps/vocabulary/migrations/0006_seed_a2_words.py` — по 12 новых слов уровня A2 для английского и немецкого (плюс колода «Продолжаем (A2)» в каждом языке)
- `?level=A1` теперь понимают `/api/words/`, `/api/review/queue/`, `/api/quiz/questions/` — везде через общий `visible_words(user, language, level)` в `apps/vocabulary/queries.py`
- Своё слово через `POST /api/words/` тоже создаётся с указанным уровнем (поле обязательное, как `part_of_speech`)

**Frontend:**
- [lib/levels.ts](frontend/src/lib/levels.ts) — общий список уровней (раньше жил только внутри `lib/grammar.ts`)
- [components/LevelSwitcher.tsx](frontend/src/components/LevelSwitcher.tsx) — переключатель уровня, вынесен в переиспользуемый компонент и подключён на `/grammar` (rewrite без изменения поведения), `/learn`, `/quiz`, `/words`
- `/learn` и `/quiz` — фильтр уровня рядом с языком, по умолчанию «Все уровни»
- `/words` — фильтр уровня над списком своих слов + выбор уровня в форме добавления (по умолчанию A1), бейдж уровня на каждой карточке слова

Текущий контент: A1 — 18 слов на язык (стартовый набор), A2 — ещё 12 на язык. B1–C2 пока не заполнены (фильтр корректно покажет пустой список).

## Дизайн и обучение грамматике

### Дизайн-система
Раньше почти весь UI был чёрно-белым (`bg-black`/`bg-white`) с ad-hoc повторением одних и тех же классов на каждой странице. Прошёлся по всему фронтенду:

- [lib/ui.ts](frontend/src/lib/ui.ts) — общие стили: `buttonClass` (primary/secondary/ghost/danger), `pillClass` (переключатели), `cardClass`, `inputClass`. Раньше эти классы были скопипащены в 8+ файлах с мелкими расхождениями — теперь один источник правды
- Акцентный цвет — indigo (было чёрный/белый), успех/ошибка — emerald/red вместо зелёного/красного «в лоб»
- [components/Navbar.tsx](frontend/src/components/Navbar.tsx) — общая шапка (лого, навигация по разделам с подсветкой активного пункта, переключатель языка, вход/выход), подключена один раз в `app/layout.tsx`. Раньше каждая страница сама рисовала «На главную»/logout/LanguageSwitcher — теперь это в одном месте
- Поправлен баг с шрифтом: `body` был жёстко на `Arial, Helvetica`, хотя Geist Sans уже подключался через переменную и просто не использовался
- Тема (`globals.css`) реагирует и на системную, и на явно выставленную (`data-theme`) тёмную/светлую схему
- Главная страница — из списка кнопок в дашборд с карточками фич (для вошедших) и лендинг с приветствием (для остальных)
- `<title>` и `<meta description>` — было дефолтное «Create Next App»

### Обучение грамматике — прогресс
Раньше раздел был чисто «почитал и забыл». Добавлено полноценное отслеживание прогресса:

- Backend: новая модель `GrammarProgress` (`apps/grammar/models.py`) — присутствие записи (user, rule) значит «изучено». `GrammarRuleSerializer` отдаёт `is_learned` для текущего пользователя; `POST /api/grammar-rules/{id}/toggle-learned/` переключает статус
- `/grammar` — полоса прогресса «X из Y изучено» на каждом уровне, галочка «✓ изучено» у пройденных правил в списке
- `/grammar/[id]` — кнопка «Отметить как изученное» прямо на странице правила, плюс навигация «← предыдущее / следующее →» внизу, чтобы проходить правила по порядку не возвращаясь к списку

Полностью проверено вживую (десктоп и мобильная раскладка): дашборд, флешкарты, квиз, список и деталь грамматики с прогрессом. Локальный Docker-деплой пересобран и обновлён.

## Расширенный словарь (английский)
По присланному списку добавлено [apps/vocabulary/migrations/0007_seed_extended_english_vocabulary.py](backend/apps/vocabulary/migrations/0007_seed_extended_english_vocabulary.py) — 268 слов на английском (было 30), 8 новых колод:

- **Глаголы** — 96 самых частых английских глаголов
- **Люди и жизнь** — person/people, man/men, woman/women, child/children и т.д.
- **Прилагательные** — 45 прилагательных (дубли из присланного списка — молодой, важный, счастливый — объединены в одно слово)
- **Фрукты** (21), **Овощи** (11), **Дом и кухня** (7 — то, что выбивалось из списка фруктов/овощей: кастрюля, диван, сковородка...)
- **Животные** — 40 названий
- **Другие слова** — числа, наречия (один, только, очень, назад...)

Пересекающиеся с уже существующими словами (to go, to eat, to speak, to buy, to understand, good, big, happy, difficult, expensive, tired, apple, time) не задублированы — слово просто получает вторую колоду через `get_or_create`, уровень и прогресс пользователя не трогаются. Миграция аккуратно обратима: при откате такие переиспользованные слова не удаляются, только отвязываются от новых колод.

Также добавлено 5 правил грамматики ([0005_seed_more_english_rules.py](backend/apps/grammar/migrations/0005_seed_more_english_rules.py)): There is/There are, предлоги места (in/on/at), some/any (A1); сравнительная и превосходная степень прилагательных, модальный can, going to (A2) — итого 15 правил для английского.

## Деплой на реальный сервер (VPS)

Локальный Docker-деплой (см. выше) уже даёт готовые образы — для реального сервера в интернете нужны ещё: домен, реверс-прокси с HTTPS и закрытые от внешнего мира порты бэкенда/базы. Для этого в репозитории есть отдельный prod-конфиг, который не трогает локальный `docker-compose.yml`:

- [docker-compose.prod.yml](docker-compose.prod.yml) — тот же backend/frontend/db + сервис `caddy` (реверс-прокси с автоматическим HTTPS через Let's Encrypt); порты 8000/5432 наружу не публикуются, наружу торчат только 80/443 у Caddy
- [Caddyfile](Caddyfile) — маршрутизация по поддоменам: `app.домен` → фронтенд, `api.домен` → бэкенд
- `.env.prod.example` (корень) и `backend/.env.prod.example` — шаблоны конфигурации

### Что нужно заранее
- VPS с Ubuntu/Debian (любой провайдер — DigitalOcean, Hetzner, Timeweb, Oracle Cloud Free и т.п.), минимум 1–2 ГБ RAM
- Домен, у которого можно добавить DNS-записи
- SSH-доступ к серверу

### Если сервер — Oracle Cloud Free (Always Free)

Настоящий бесплатный навсегда VPS, но с парой особенностей по сравнению с обычным провайдером:

1. **Регистрация:** [cloud.oracle.com/free](https://www.oracle.com/cloud/free/) — понадобится карта для верификации личности (списаний по Always Free тарифу не будет).
2. **Создание VM:** Compute → Instances → Create Instance. Выберите **Always Free eligible** shape:
   - Рекомендую **VM.Standard.A1.Flex** (ARM, до 4 OCPU / 24 ГБ RAM бесплатно навсегда — с запасом на Postgres + Django + Next.js) — 2 OCPU / 12 ГБ вполне достаточно
   - Если в вашем регионе A1 недоступен («Out of capacity») — попробуйте другой регион при создании аккаунта, либо возьмите **VM.Standard.E2.1.Micro** (слабее, 1 ГБ RAM, но тоже бесплатно навсегда)
   - Образ: Ubuntu 22.04 или 24.04
   - При создании сгенерируйте/скачайте SSH-ключ — он единственный способ попасть на сервер
3. **Сеть — самое частое место, где всё «не работает»:** у Oracle Cloud два независимых файрвола, и открыть нужно оба:
   - **Security List** в облаке: VCN → ваша сеть → Security Lists → Default Security List → Add Ingress Rules → разрешить TCP 80 и 443 от `0.0.0.0/0` (порт 22 обычно уже открыт)
   - **iptables на самой VM** (Oracle предустанавливает свои правила): подключитесь по SSH и выполните
     ```bash
     sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
     sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
     sudo netfilter-persistent save
     ```
   Если пропустить второй пункт — DNS и Security List будут в порядке, а сайт всё равно не откроется снаружи.
4. Дальше — обычные шаги ниже, ничего специфичного для Oracle там уже нет.

### Шаги

**1. DNS.** Создайте две A-записи, указывающие на IP сервера: `app.вашдомен.com` и `api.вашдомен.com`.

**2. Установите Docker на сервере:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # чтобы не писать sudo перед каждой командой docker
```
После `usermod` перезайдите по SSH (или выполните `newgrp docker`), иначе группа не применится.

**3. Скопируйте проект на сервер** (с локальной машины, из корня репозитория). Для Oracle Cloud: пользователь `ubuntu`, и нужен ключ, скачанный при создании VM — добавьте `-e "ssh -i /path/to/key.pem"`:
```bash
rsync -avz --exclude node_modules --exclude .venv --exclude .next --exclude __pycache__ \
  -e "ssh -i /path/to/key.pem" \
  ./ ubuntu@your-server-ip:/opt/poliglot/
```
(на других провайдерах обычно просто `user@your-server-ip` без `-e`, если вход по паролю или уже добавленному в агент ключу)

**4. На сервере — заполните конфиги:**
```bash
cd /opt/poliglot
cp .env.prod.example .env.prod              # APP_DOMAIN, API_DOMAIN, POSTGRES_PASSWORD, GOOGLE_OAUTH_CLIENT_ID
cp backend/.env.prod.example backend/.env.prod   # SECRET_KEY, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, GOOGLE_OAUTH_CLIENT_ID
```
Впишите реальные домены и придумайте новый `SECRET_KEY` (например: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`) и `POSTGRES_PASSWORD`.

**5. Запустите:**
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
```
Caddy сам получит и продлит TLS-сертификат от Let's Encrypt для обоих доменов — ничего дополнительно настраивать не нужно.

**6. Google OAuth.** В Google Cloud Console → Credentials → ваш OAuth-клиент → добавьте `https://app.вашдомен.com` в Authorized JavaScript origins.

**7. Проверка:** откройте `https://app.вашдомен.com` — должна открыться главная страница. Зарегистрируйтесь, проверьте `/learn`.

### Без домена — сразу по IP

Если домена пока нет, есть отдельный, более простой конфиг: [docker-compose.ip.yml](docker-compose.ip.yml) — без Caddy и HTTPS, фронтенд и бэкенд просто торчат наружу на портах 3000 и 8000 (как в локальном `docker-compose.yml`, только на публичном сервере). Ограничения: без замочка (`http://`, не `https://`) и вход через Google, скорее всего, не заработает — Google обычно не разрешает IP в Authorized JavaScript origins. Email/пароль работает как обычно.

Пример ниже — с уже подставленным IP `45.130.166.187` (Kamatera, Tokyo, 2 vCPU/4 ГБ). Для другого сервера замените IP на свой везде.

**1. Установите Docker на сервере** (как в шаге 2 выше, `curl -fsSL https://get.docker.com | sh` + `usermod`).

**2. Откройте порты.** В панели Kamatera → Networks/Firewall для этого сервера разрешите **22** (SSH), **3000** и **8000** (TCP, от `0.0.0.0/0`). На самой VM:
```bash
sudo ufw allow 22/tcp && sudo ufw allow 3000/tcp && sudo ufw allow 8000/tcp && sudo ufw --force enable
```

**3. Скопируйте проект на сервер:**
```bash
rsync -avz --exclude node_modules --exclude .venv --exclude .next --exclude __pycache__ \
  ./ root@45.130.166.187:/opt/poliglot/
```
(Kamatera обычно даёт доступ по паролю от root на Ubuntu-образах — если настроен SSH-ключ, добавьте `-e "ssh -i /path/to/key"`)

**4. На сервере — заполните конфиги:**
```bash
cd /opt/poliglot
cp .env.ip.example .env.ip                    # SERVER_IP уже = 45.130.166.187, впишите POSTGRES_PASSWORD
cp backend/.env.ip.example backend/.env.ip     # впишите SECRET_KEY (см. команду в шаге 4 выше)
```

**5. Запустите:**
```bash
docker compose -f docker-compose.ip.yml --env-file .env.ip up --build -d
```

**6. Проверка:** откройте `http://45.130.166.187:3000` — должна открыться главная страница «Полиглот». API — на `http://45.130.166.187:8000/api/health/`.

Домен можно подключить в любой момент позже — тогда просто переходите на `docker-compose.prod.yml` из шагов выше (тот же сервер, тот же Docker, ничего пересоздавать не нужно).

### Обновление после изменений в коде
```bash
rsync -avz --exclude node_modules --exclude .venv --exclude .next --exclude __pycache__ \
  ./ user@your-server-ip:/opt/poliglot/
ssh user@your-server-ip "cd /opt/poliglot && docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d"
```

### Дополнительно (рекомендуется)
- Файрвол: `ufw allow 22,80,443/tcp && ufw enable` — остальные порты закрыть
- Бэкапы Postgres: `docker compose -f docker-compose.prod.yml exec db pg_dump -U poliglot poliglot > backup.sql` (по крону)
- Вместо `rsync` можно деплоить через `git pull` — проект теперь в собственном репозитории: [github.com/kalilovnurbolot/poliglot](https://github.com/kalilovnurbolot/poliglot) (публичный, клонируется без авторизации)

## Мобильная адаптация
Проверка на 375px (iPhone) вскрыла несколько реальных багов вёрстки — все из-за длинного контента (см. «Расширенный словарь» и учебник ниже) или изначально не продуманных узких экранов:

- [FlashCard.tsx](frontend/src/components/FlashCard.tsx) — подсказки «← не знаю / знаю →» были жёстко закреплены по центру карточки и накладывались на текст у длинных фраз («Could I have (your phone number), please?»). Подсказки вынесены за пределы карточки (сверху), плюс шрифт слова/перевода уменьшается адаптивно по длине текста
- [Navbar.tsx](frontend/src/components/Navbar.tsx) — кнопки «Войти/Регистрация» для неавторизованных вылезали за край экрана на мобильном вместо переноса; переверстано в устойчивые два ряда (лого+переключатели сверху, навигация по разделам снизу)
- [words/page.tsx](frontend/src/app/words/page.tsx) — форма добавления слова была жёстко в 2 колонки, из-за чего плейсхолдер «Транскрипция (необязательно)» обрезался на узком экране; теперь одна колонка на мобильном, две — от `sm:`
- [grammar/[id]/page.tsx](frontend/src/app/grammar/%5Bid%5D/page.tsx) — markdown-таблицы обёрнуты в `overflow-x-auto` (защита от переполнения на случай широкой таблицы)

Проверено на светлой и тёмной теме, viewport 375×812.

## PWA (устанавливаемое приложение)
- [app/manifest.ts](frontend/src/app/manifest.ts) — манифест (название, standalone-режим, цвета, иконки 192/512)
- Иконки генерируются на этапе сборки через `next/og` (`ImageResponse`) — не нужны внешние файлы-картинки: [icon.tsx](frontend/src/app/icon.tsx) (favicon), [apple-icon.tsx](frontend/src/app/apple-icon.tsx) (180×180 для iOS), [icon-192.png/route.tsx](frontend/src/app/icon-192.png/route.tsx) и [icon-512.png/route.tsx](frontend/src/app/icon-512.png/route.tsx) (для манифеста) — везде буква «П» на индиго-фоне (`#4f46e5`, наш акцентный цвет)
- `layout.tsx` — `appleWebApp` метаданные (заголовок, статус-бар) и `theme-color` отдельно для светлой/тёмной темы
- [public/sw.js](frontend/public/sw.js) — простой service worker: network-first для страниц (чтобы онлайн всегда была свежая версия), cache-first для статики `_next/static` и картинок/шрифтов; **никогда не трогает чужой origin** — API живёт на другом порту/домене, поэтому его ответы физически не попадают в кеш. Регистрируется только в production через [ServiceWorkerRegistration.tsx](frontend/src/components/ServiceWorkerRegistration.tsx)
- Старый дефолтный `favicon.ico` от `create-next-app` удалён — иконка теперь только своя

**Важно:** и установка на главный экран, и service worker требуют HTTPS (браузеры делают исключение только для `localhost`). На текущем деплое по голому IP (`docker-compose.ip.yml`, `http://45.130.166.187:3000`) файлы манифеста/иконок отдаются корректно, но сама установка приложения и регистрация service worker в браузере, скорее всего, не заработают — это ограничение браузера (secure context), не баг. Заработает полностью, как только подключите домен + Caddy (`docker-compose.prod.yml`, автоматический HTTPS — см. «Деплой на реальный сервер» выше).
