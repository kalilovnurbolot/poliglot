# Полиглот

Приложение для изучения языков: заучивание слов свайпами, грамматика для начинающих, квизы (в т.ч. на слух). Языки: английский и немецкий.

## Стек

Один Django-проект в [backend/](backend/) — и бэкенд, и фронтенд. Отдельного SPA/Node-сервера нет.

- **Django-шаблоны** — все страницы рендерятся на сервере ([apps/web/](backend/apps/web/))
- **Tailwind CSS** — собирается один раз в статический `app.css` (Node в рантайме не нужен)
- **Ванильный JS** — только там, где без него никак: свайп-карточки, квиз, живое превью редактора правил
- **Django REST Framework** — JSON API (`/api/...`) остался: им пользуются JS-страницы (через сессию + CSRF) и его можно дёргать снаружи по JWT
- Авторизация — обычные Django-сессии (`login()`), плюс вход через Google Identity Services

## Запуск (локально, sqlite, без Docker)

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Открыть http://localhost:8000 — это и сайт, и API (`/api/`), и админка (`/admin/`).

Админ: аккаунт с email из `ADMIN_EMAILS` (по умолчанию `kalilovnurbolot3@gmail.com`) автоматически становится суперпользователем при регистрации, либо `python manage.py createsuperuser`.

Тесты: `python manage.py test`

## Стили (Tailwind)

Исходник — [apps/web/tailwind/input.css](backend/apps/web/tailwind/input.css), результат — `apps/web/static/web/css/app.css` (лежит в git, поэтому для запуска ничего собирать не нужно). Пересобрать после того, как в шаблонах/JS появились новые классы:

```bash
cd backend
npx @tailwindcss/cli@4 -i apps/web/tailwind/input.css -o apps/web/static/web/css/app.css --minify
```

Если Node не установлен — можно [standalone-бинарник Tailwind](https://github.com/tailwindlabs/tailwindcss/releases) (`tailwindcss -i ... -o ... --minify`, те же аргументы). Повторяющиеся наборы классов вынесены в компоненты в `input.css`: `.btn` (`.btn-primary/-secondary/-ghost/-danger`), `.pill` (`.pill-active`), `.card`, `.input`.

## Запуск с Postgres (без остального Docker)

```bash
docker compose up -d db
```

Затем в `backend/.env` раскомментировать `DATABASE_URL` и выполнить `python manage.py migrate`.

## Локальный деплой (Docker Compose, production-режим)

Postgres + Django/gunicorn одной командой:

```bash
cp backend/.env.docker.example backend/.env.docker   # SECRET_KEY, GOOGLE_OAUTH_CLIENT_ID
docker compose up --build -d
```

Сайт: http://localhost:8018. При старте контейнер сам накатывает миграции и собирает статику ([entrypoint.sh](backend/entrypoint.sh)); статика раздаётся через `whitenoise`.

```bash
docker compose logs -f          # логи
docker compose down             # остановить (данные Postgres сохранятся в volume)
docker compose down -v          # остановить и стереть данные Postgres
docker compose up --build -d    # пересобрать после изменений в коде
docker compose exec backend python manage.py createsuperuser
```

## Структура

```
backend/
  config/            настройки, корневые urls
  apps/core/         Language (en, de), Level (A1–C2), /api/health/
  apps/users/        кастомный User (логин по email), регистрация, Google OAuth (google.py)
  apps/vocabulary/   Deck, Word, UserWordProgress, SRS (srs.py), очередь повторения (queries.py)
  apps/grammar/      GrammarRule, GrammarProgress
  apps/quizzes/      генерация вопросов квиза (questions.py), без своих моделей
  apps/web/          весь UI: views, формы, шаблоны, статика
    rule_render.py     Markdown правила → HTML (блоки formula/example/note/…)
    templates/web/     страницы и partials (navbar, level_switcher, …)
    static/web/        css (Tailwind), js, иконки PWA, service worker
```

Логика (очередь повторения, вопросы квиза, проверка Google-токена) живёт в функциях внутри доменных приложений и используется одновременно HTML-страницами и API.

## Страницы

| URL | Что | Доступ |
|---|---|---|
| `/` | лендинг / дашборд | все |
| `/login/`, `/register/`, `/logout/` | вход по email/паролю или через Google | все |
| `/learn/`, `/learn/<A1…C2\|all>/` | выбор уровня → карточки со свайпами | вошедшие |
| `/quiz/?level=&mode=translation\|listening` | квиз: выбор перевода или на слух | вошедшие |
| `/grammar/?level=A1` | список правил с прогрессом | все |
| `/grammar/<id>/` | правило: оглавление разделов, «изучено», пред./след. | все |
| `/grammar/new/`, `/grammar/<id>/edit/` | редактор правила с живым превью | админ (`is_staff`) |
| `/words/?level=` | свои слова: добавить / удалить | вошедшие |

Изучаемый язык выбирается в шапке и хранится в сессии.

## Экран заучивания слов

SRS по системе Лейтнера ([srs.py](backend/apps/vocabulary/srs.py)): 8 «коробок» (0–7) с растущими интервалами — от 10 минут до 30 дней. Очередь: слова, которым пора на повтор (`next_review_at <= now`), плюс новые, если очередь не заполнена.

Свайп карточки (мышью, пальцем или стрелками ←/→/↑/↓), клик — перевернуть:
- **→ знаю** — `box_level += 1`, следующий повтор позже
- **← не знаю** — `box_level = 0`, вернётся через 10 минут
- **↑ избранное** — ставит `is_favorite`, не трогает box/счётчики
- **↓ пропустить** — карточка уходит в конец очереди, на сервер ничего не отправляется

Очередь отдаётся сервером прямо в шаблон (`json_script`), ответы уходят в `POST /api/review/answer/` ([learn.js](backend/apps/web/static/web/js/learn.js)).

## Квиз

4 варианта перевода (1 верный + 3 случайных). Слова берутся в первую очередь из уже встреченных в карточках; если таких меньше 4 — из всего доступного пула. Ответ проверяется в браузере и отправляется в тот же `POST /api/review/answer/` (`right`/`left`), поэтому квиз питает тот же SRS-прогресс, что и карточки. Режим «На слух» озвучивает слово через Web Speech API (`en-US`/`de-DE`).

## Грамматика

Правила пишутся в Markdown с дополнительными блоками, рендер — на сервере ([rule_render.py](backend/apps/web/rule_render.py), `markdown-it-py`):

- `## Раздел` — попадает в боковое оглавление
- ` ```formula ` — формулы, роли слов `[s: …]` подлежащее, `[v: …]` глагол, `[o: …]` дополнение, `[m: …]` уточнение, `[f: …]` служебное слово
- ` ```example ` — пример с разметкой ролей, строка с `=` — перевод
- ` ```note ` — заметка (`× | …` — частая ошибка), ` ```legend `, ` ```pills `, ` ```cards `
- обычные таблицы, списки, `**жирный**`, `` `код` ``; сырой HTML не исполняется

Добавлять/редактировать/удалять правила может только админ; отметка «изучено» — любой вошедший пользователь.

## API

Системные объекты (`owner = null`) видны всем и доступны только на чтение; свои объекты может редактировать только владелец. Авторизация — сессия (для страниц сайта) или JWT `Authorization: Bearer <access>`.

- `GET /api/health/`, `GET /api/languages/`
- `GET/POST /api/decks/`, `GET/PUT/PATCH/DELETE /api/decks/{id}/` — `?language=en`, `?mine=true`
- `GET/POST /api/words/`, `GET/PUT/PATCH/DELETE /api/words/{id}/` — `?language=en&level=A1&deck={id}&mine=true`
- `GET /api/review/queue/?language=en&level=A1&limit=20`, `POST /api/review/answer/` (`{word, direction}`), `GET /api/review/favorites/`
- `GET /api/quiz/questions/?language=en&level=A1&limit=10`
- `GET /api/grammar-rules/?language=en&level=A1`, `POST/PATCH/DELETE` — только админ, `POST /api/grammar-rules/{id}/toggle-learned/`
- `POST /api/auth/register/`, `POST /api/auth/login/`, `POST /api/auth/refresh/`, `POST /api/auth/google/`, `GET /api/auth/me/` — JWT для внешних клиентов

### Google OAuth

Схема с ID-токеном (Google Identity Services), поэтому **client secret не нужен** — только публичный `client_id` в `backend/.env`: `GOOGLE_OAUTH_CLIENT_ID=...`. Кнопка входа показывается, только если он задан. Браузер получает id_token от Google и отправляет его на `/auth/google/`, сервер проверяет его через `google-auth` и логинит пользователя в сессию. Файл `client_secret_*.json` не используется и **не должен попадать в git**.

## Контент

- Языки: английский и немецкий (`apps/core/migrations/0003_seed_german_language.py`). Новый язык — это только data-миграции (Language + слова + правила), без изменений кода
- Слова: стартовые колоды A1/A2 для обоих языков, расширенный английский словарь и слова по юнитам учебника (миграции `apps/vocabulary/migrations/0003…0009`)
- Грамматика: правила A1/A2 для обоих языков (миграции `apps/grammar/migrations/0002…0007`)

### Расширенный словарь (английский)
По присланному списку добавлено [0007_seed_extended_english_vocabulary.py](backend/apps/vocabulary/migrations/0007_seed_extended_english_vocabulary.py) — 268 слов на английском (было 30), 8 новых колод:

- **Глаголы** — 96 самых частых английских глаголов
- **Люди и жизнь** — person/people, man/men, woman/women, child/children и т.д.
- **Прилагательные** — 45 прилагательных (дубли из присланного списка — молодой, важный, счастливый — объединены в одно слово)
- **Фрукты** (21), **Овощи** (11), **Дом и кухня** (7 — то, что выбивалось из списка фруктов/овощей: кастрюля, диван, сковородка...)
- **Животные** — 40 названий
- **Другие слова** — числа, наречия (один, только, очень, назад...)

Пересекающиеся с уже существующими словами (to go, to eat, to speak, to buy, to understand, good, big, happy, difficult, expensive, tired, apple, time) не задублированы — слово просто получает вторую колоду через `get_or_create`, уровень и прогресс пользователя не трогаются. Миграция аккуратно обратима: при откате такие переиспользованные слова не удаляются, только отвязываются от новых колод.

Также добавлено 5 правил грамматики ([0005_seed_more_english_rules.py](backend/apps/grammar/migrations/0005_seed_more_english_rules.py)): There is/There are, предлоги места (in/on/at), some/any (A1); сравнительная и превосходная степень прилагательных, модальный can, going to (A2) — итого 15 правил для английского.


## Деплой на реальный сервер (VPS)

Для сервера в интернете есть отдельный prod-конфиг, который не трогает локальный `docker-compose.yml`:

- [docker-compose.prod.yml](docker-compose.prod.yml) — backend + db + `caddy` (реверс-прокси с автоматическим HTTPS через Let's Encrypt); наружу торчат только 80/443
- [Caddyfile](Caddyfile) — `app.домен` → Django
- `.env.prod.example` (корень) и `backend/.env.prod.example` — шаблоны конфигурации

### Что нужно заранее
- VPS с Ubuntu/Debian (DigitalOcean, Hetzner, Timeweb, Oracle Cloud Free и т.п.), от 1 ГБ RAM
- Домен, у которого можно добавить DNS-записи
- SSH-доступ к серверу

### Если сервер — Oracle Cloud Free (Always Free)

Настоящий бесплатный навсегда VPS, но с парой особенностей по сравнению с обычным провайдером:

1. **Регистрация:** [cloud.oracle.com/free](https://www.oracle.com/cloud/free/) — понадобится карта для верификации личности (списаний по Always Free тарифу не будет).
2. **Создание VM:** Compute → Instances → Create Instance. Выберите **Always Free eligible** shape:
   - Рекомендую **VM.Standard.A1.Flex** (ARM, до 4 OCPU / 24 ГБ RAM бесплатно навсегда — с запасом на Postgres + Django) — 2 OCPU / 12 ГБ вполне достаточно
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

**1. DNS.** Создайте A-запись `app.вашдомен.com`, указывающую на IP сервера.

**2. Установите Docker на сервере:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # чтобы не писать sudo перед каждой командой docker
```
После `usermod` перезайдите по SSH (или выполните `newgrp docker`).

**3. Скопируйте проект на сервер** (или `git clone`). Для Oracle Cloud: пользователь `ubuntu` и ключ, скачанный при создании VM:
```bash
rsync -avz --exclude .venv --exclude __pycache__ --exclude db.sqlite3 \
  -e "ssh -i /path/to/key.pem" \
  ./ ubuntu@your-server-ip:/opt/poliglot/
```

**4. На сервере — заполните конфиги:**
```bash
cd /opt/poliglot
cp .env.prod.example .env.prod                   # APP_DOMAIN, POSTGRES_PASSWORD
cp backend/.env.prod.example backend/.env.prod   # SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, GOOGLE_OAUTH_CLIENT_ID
```
Новый `SECRET_KEY`: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`.

**5. Запустите:**
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
```
Caddy сам получит и продлит TLS-сертификат.

**6. Google OAuth.** В Google Cloud Console → Credentials → ваш OAuth-клиент → добавьте `https://app.вашдомен.com` в Authorized JavaScript origins.

**7. Проверка:** откройте `https://app.вашдомен.com`, зарегистрируйтесь, проверьте `/learn/`.

### Без домена — сразу по IP

[docker-compose.ip.yml](docker-compose.ip.yml) — без Caddy и HTTPS, Django торчит наружу на порту 8000. Ограничения: `http://` без замочка, PWA и вход через Google, скорее всего, не заработают (Google не разрешает IP в Authorized JavaScript origins). Email/пароль работает.

Пример — с IP `45.130.166.187` (замените на свой):

1. Установите Docker (как в шаге 2 выше).
2. Откройте порты 22 и 8000 в панели провайдера и на VM: `sudo ufw allow 22/tcp && sudo ufw allow 8000/tcp && sudo ufw --force enable`
3. Скопируйте проект (как в шаге 3 выше).
4. Конфиги:
   ```bash
   cd /opt/poliglot
   cp .env.ip.example .env.ip                  # POSTGRES_PASSWORD
   cp backend/.env.ip.example backend/.env.ip  # SECRET_KEY, ALLOWED_HOSTS=<IP>, CSRF_TRUSTED_ORIGINS=http://<IP>:8000
   ```
5. `docker compose -f docker-compose.ip.yml --env-file .env.ip up --build -d`
6. Откройте `http://45.130.166.187:8000`.

Домен можно подключить позже — просто переходите на `docker-compose.prod.yml`.

### Обновление после изменений в коде
```bash
rsync -avz --exclude .venv --exclude __pycache__ --exclude db.sqlite3 ./ user@your-server-ip:/opt/poliglot/
ssh user@your-server-ip "cd /opt/poliglot && docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d"
```

### Дополнительно (рекомендуется)
- Файрвол: `ufw allow 22,80,443/tcp && ufw enable` — остальные порты закрыть
- Бэкапы Postgres: `docker compose -f docker-compose.prod.yml exec db pg_dump -U poliglot poliglot > backup.sql` (по крону)
- Деплой через `git pull` — репозиторий: [github.com/kalilovnurbolot/poliglot](https://github.com/kalilovnurbolot/poliglot)

## PWA (устанавливаемое приложение)

- `/manifest.webmanifest` — манифест (название, standalone-режим, цвета, иконки 192/512 из `static/web/icons/`)
- `/sw.js` — service worker ([исходник](backend/apps/web/static/web/js/sw.js)), отдаётся с корня сайта, чтобы его scope покрывал все страницы: network-first для страниц, cache-first для `/static/` (имена файлов с хешем, поэтому кэш безопасен); `/api/` и `/admin/` никогда не кэшируются. На `localhost` не регистрируется, чтобы не мешать разработке
- Установка на главный экран и service worker требуют HTTPS (кроме `localhost`) — на деплое по голому IP не заработают, с доменом + Caddy — да
