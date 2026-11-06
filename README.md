# NovaAltairBot

Телеграм-бот для сервиса NovaAltair: человек нажимает `/start`, получает аккаунт,
берёт пробную подписку и смотрит свой ключ 3x-ui в личном кабинете. Бот не лезет
в панель сам — он ходит по HTTP в [NovaAltairApi](https://github.com/Rimuru3573/NovaAltairApi),
а та уже создаёт пользователей и ключи в 3x-ui.

Собрано на aiogram 3.31 (long polling) и aiohttp, настройки — pydantic-settings,
зависимости — uv, запуск — Docker Compose.

<p align="center">
  <img src="assets/Altair_main_page_v4.jpg" width="720" alt="Главное меню бота">
</p>

## Что уже работает

- **Регистрация по `/start`.** API создаёт пользователя с логином `user_<telegram_id>`,
  бот один раз присылает логин и пароль. Пароль нигде не хранится, так что
  сохранить его нужно сразу — об этом бот честно предупреждает в сообщении.
- **Пробная подписка.** Выдаётся через API на `FREE_TRIAL_DAYS` дней. Повторно
  её не получить: на `409` бот отвечает «Ах ты шалунишка, ты уже использовал
  пробный период!».
- **Просмотр ключа.** Ссылка на подписку, срок действия и кнопка «Скопировать
  ссылку» — Telegram копирует её сам, без возни с буфером обмена.
- **Профиль.** Telegram-ник, username, дата окончания, `payment_id`, ссылки на
  соглашение и политику.
- **Реферальные ссылки.** `/start ref_<telegram_id>` передаёт `referred_by_id`
  в API — сама механика начисления ещё не готова, но переход уже учитывается.

## Что пока не работает

Кнопки «Продление», «Пригласить», «Подключиться» и «Перевыпустить» отвечают
«функция ещё не добавлена, но совсем скоро реализуется». `admin_handlers.py` и
`payments.py` — пустые роутеры, `states/state.py` тоже пустой: FSM появится
вместе с оплатой и продлением.

То есть сейчас это рабочий скелет магазина: аккаунты, пробный период и выдача
ключа есть, денег он пока не принимает.

## Как это связано с API

```
Telegram  →  NovaAltairBot  →  NovaAltairApi  →  3x-ui
             (aiogram)         (FastAPI)         (панель)
```

Бот использует четыре запроса: создать пользователя, создать ключ, получить ключ
по email и снять флаг «новый» (в клиенте есть ещё `get_user`, но пока он никому
не понадобился). Тонкий клиент живёт в
`src/novaaltairbot/api/api.py`, а HTTP-статусы (`404`, `409`, `500`) превращаются
в исключения из `errors.py` — поэтому в хендлерах их можно ловить по-человечески,
а не разбирать ответы вручную.

## Запуск

Нужен Python 3.14, [uv](https://docs.astral.sh/uv/), поднятый NovaAltairApi и
токен от [@BotFather](https://t.me/BotFather).

### Локально

```bash
git clone https://github.com/Rimuru3573/NovaAltairBot.git
cd NovaAltairBot

uv sync
cp .env.example .env
# заполнить BOT, BOT_API_KEY, API_PATH, FREE_TRIAL_DAYS

uv run python -m novaaltairbot.main
```

Запускать нужно из корня репозитория: картинка главного меню подхватывается по
относительному пути `./assets/Altair_main_page_v4.jpg`.

### Docker

```bash
docker compose up -d --build
docker compose logs -f
docker compose down
```

Обновление после `git pull` — той же командой `docker compose up -d --build`.
`.env` в образ не копируется, переменные прокидываются через `env_file`.

### API в контейнере на той же машине

Внутри контейнера `localhost` — это сам контейнер, поэтому в `.env` бота нужно
указать хост, а не `127.0.0.1`:

```dotenv
API_PATH=http://host.docker.internal:8000
```

`host.docker.internal` уже прописан в `docker-compose.yml` через
`extra_hosts: host-gateway`, так что на Linux он тоже работает. У API при этом
должен быть опубликован порт (`ports: - "8000:8000"`) и uvicorn должен слушать
`0.0.0.0` — иначе снаружи контейнера до него не достучаться.

Если публиковать порт наружу не хочется, контейнеры можно связать общей сетью и
ходить по имени сервиса:

```bash
docker network create nova
```

```yaml
# в обоих docker-compose.yml
services:
  api:
    networks: [nova]
networks:
  nova:
    external: true
```

```dotenv
# .env бота
API_PATH=http://api:8000
```

## Настройки

Всё читается из `.env` через pydantic-settings. Шаблон — `.env.example`.

| Переменная        | Обязательна | Что это                                              |
| ----------------- | ----------- | ---------------------------------------------------- |
| `BOT`             | да          | токен бота от @BotFather                             |
| `BOT_API_KEY`     | да          | ключ для заголовка `X-API-Key`, должен совпадать с API |
| `API_PATH`        | да          | базовый URL API, например `http://127.0.0.1:8000`    |
| `FREE_TRIAL_DAYS` | да          | сколько дней даётся в пробном периоде                |
| `PROXY`           | нет         | SOCKS/HTTP-прокси для Telegram API                   |

## Структура

```
NovaAltairBot/
├── src/novaaltairbot/
│   ├── main.py              # логи, роутеры, polling
│   ├── config.py            # настройки из .env
│   ├── lexicon.py           # все тексты сообщений
│   ├── errors.py            # исключения под ошибки API
│   ├── api/
│   │   ├── api.py           # HTTP-клиент NovaAltairApi
│   │   └── schemas.py       # pydantic-модели
│   ├── handlers/
│   │   ├── user_handlers.py # /start, пробный период, ключ, профиль
│   │   ├── admin_handlers.py
│   │   └── payments.py
│   ├── keyboards/
│   │   └── inline.py        # инлайн-клавиатуры
│   └── states/
│       └── state.py
├── assets/                  # картинки для сообщений
├── tests/                   # пока почти всё закомментировано
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

## Логи

Пишутся в stdout и в `bot.log` с ротацией (5 МБ × 3 файла). В Docker `bot.log`
лежит внутри контейнера, а смотреть удобнее так:

```bash
docker compose logs -f
```

## Тесты

```bash
uv run pytest
```

Сейчас в `tests/test_api.py` оба теста закомментированы: они ходят в живой API и
создают реального пользователя, так что просто так их не запустить.

## Связь

Поддержка — [@zxcurs4d](https://t.me/zxcurs4d), она же кнопкой в боте.
API и работа с 3x-ui лежат в отдельном репозитории:
[NovaAltairApi](https://github.com/Rimuru3573/NovaAltairApi).
