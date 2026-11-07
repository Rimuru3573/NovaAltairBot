# Аудит NovaAltairBot

**Снимок:** коммит `7aa208e` («remove telegram_id»), рабочее дерево на 06.11.2026 ~20:15
**Объём:** все 15 python-файлов (`src/novaaltairbot`), `tests/`, конфиги, Docker, `bot.log` (3358 строк)
**Важно:** во время аудита файлы `schemas.py` и `user_handlers.py` изменились (20:10) и появился коммит `7aa208e`. Отчёт соответствует **последнему** состоянию; если будете править дальше — сверяйте номера строк.

---

## Как проверял

1. Прочитал все файлы пакета и конфиги (повторно — после изменения `schemas.py`/`user_handlers.py`).
2. `python -m compileall` — успешно; `pytest` — **0 тестов, exit code 5**.
3. AST-анализ: дубли имён функций, «мёртвые» callback-кнопки, star-imports.
4. Репро-скрипты с фейковыми `Message`/`CallbackQuery`/API — подтвердили падения в хендлерах (ниже помечено «подтверждено»).
5. Разбор `bot.log`: 318 строк `ERROR`/`CRITICAL`, **30 блоков трейсбеков**, 76 × `TelegramUnauthorizedError`, 65 × `ServerDisconnected`, прокси-ошибки, `TelegramBadRequest`, `ValidationError`, `ContentTypeError`, `KeyError`, `TypeError`, `AttributeError`.
6. Сверка контракта с реальным кодом `NovaAltairApi` (router, schemas, repository, models, db, xui, security с GitHub) — статусы, поля, FK, авторизация.

Временные скрипты лежали в `.tmp_audit/` и удалены; в коммит `7aa208e` они попали случайно (см. «Хвосты» в конце).

---

## Сводка

| Приоритет | Кол-во | Что это |
|---|---|---|
| **P0** | 6 | Падения, потеря пользователя/ключа, тихий отказ бота |
| **P1** | 13 | Логические ошибки и сломанный UX |
| **P2** | 21 | Надёжность, эксплуатация, безопасность, тесты/CI |
| **P3** | — | Чего не хватает как продукта (оплата, продление, рефералка, админка) |

---

# P0 — ломает основной сценарий

## P0-1. `edit_caption` на сообщении без подписи → `Bad Request: message text is empty`

**Где:** `src/novaaltairbot/handlers/user_handlers.py:34`, `81`, `92`, `97`, `108`, `113`, `120`, `127`, `135`, `141`, `147`, `154`

**Симптом:** нажатие «Назад»/«Инструкция»/«Продлить» на текстовом сообщении (а не на фото главного меню) не делает ничего — в логе `TelegramBadRequest: message text is empty`. В `bot.log` это самая частая логическая ошибка: **7 повторов** на `back_main_page_photo`.

**Почему:** все экраны редактируются через `callback.message.edit_caption(...)`, но подпись есть только у сообщения-фото. Ветка «Ах ты шалунишка…» (`:74`) и любые ответы через `answer(text=...)` создают **текстовое** сообщение с кнопкой «Назад» — и она гарантированно падает. Воспроизведено локально (кейсы D, G, K): «Назад» с текстового сообщения → `RuntimeError: TelegramBadRequest: message text is empty`.

**Почему это критично:** пользователь попадает в тупик: кнопка есть, реакции нет.

**Как чинить:** один общий рендер, который умеет и `edit_text`, и `edit_caption`, плюс перехват `TelegramBadRequest`:

```python
from aiogram.exceptions import TelegramBadRequest

async def render(callback: CallbackQuery, text: str, kb: InlineKeyboardMarkup) -> None:
    message = callback.message
    try:
        if getattr(message, "caption", None) is not None:
            await message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await message.edit_text(text=text, parse_mode="HTML", reply_markup=kb)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc):
            return
        await message.answer(
            text, parse_mode="HTML", reply_markup=kb,
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
```

---

## P0-2. Нет ни одного глобального обработчика ошибок

**Где:** `src/novaaltairbot/main.py:20-31` (`dp.errors` не зарегистрирован)

**Симптом:** любое исключение в хендлере = пользователь не получает **ничего**, в лог уходит трейсбек. В `bot.log` — 30 таких блоков, ни один не обработан.

**Почему:** aiogram логирует исключение и молча роняет обработку апдейта; `callback.answer()` уже вызван, поэтому у пользователя просто «ничего не произошло».

**Как чинить:**

```python
from aiogram.types import ErrorEvent

@dp.errors()
async def on_error(event: ErrorEvent) -> bool:
    log.exception("update failed", exc_info=event.exception)
    update = event.update
    if update.callback_query:
        await update.callback_query.answer("Ошибка, попробуйте позже", show_alert=True)
    target = update.message or getattr(update.callback_query, "message", None)
    if target:
        try:
            await event.bot.send_message(
                target.chat.id,
                "😔 Сервис временно недоступен. Попробуйте ещё раз через минуту.",
            )
        except Exception:  # пользователь мог заблокировать бота
            pass
    return True
```

Плюс тексты ошибок в `lexicon.py` (сейчас в словаре нет ни одной строки про ошибки).

---

## P0-3. Ошибки сети и HTTP не превращаются в доменные исключения

**Где:** `src/novaaltairbot/api/api.py:26-74`

**Симптом:** `raise Exception()` на любой неожиданный статус, а `aiohttp.ClientError`/`asyncio.TimeoutError` вообще не перехватываются. В логе: `ClientConnectorError` (API лежал на `127.0.0.1:8000`) и `ContentTypeError` — сырые трейсбеки, пользователь без ответа.

**Почему:** клиент разбирает только «счастливые» статусы; на 401 (неверный `BOT_API_KEY`), 422 (валидация FastAPI), 500 без JSON и на обрыв сети — всё валится наружу. Подтверждено локально (кейс B).

**Как чинить:** один `_request` с проверкой статуса, `content_type` и перехватом сетевых ошибок:

```python
class ApiUnavailable(Exception):
    """API недоступен/таймаут — временная ошибка."""

class ApiError(Exception):
    def __init__(self, status: int, method: str, body: str = "") -> None:
        super().__init__(f"{method} -> {status}: {body[:300]}")
        self.status, self.method, self.body = status, method, body

async def _request(self, method: str, path: str, **kwargs) -> Any:
    if self.session is None:
        raise RuntimeError("NovaAltairApi used outside 'async with'")
    try:
        async with self.session.request(method, path, **kwargs) as response:
            body = await response.text()
            if response.status >= 400:
                raise ApiError(response.status, f"{method} {path}", body)
            return json.loads(body)
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        raise ApiUnavailable(f"{method} {path}") from exc
```

Дальше в методах — `except ApiError as exc: if exc.status == 409: ...`, а в хендлерах ловить `ApiError`/`ApiUnavailable` по-человечески.

---

## P0-4. Пробный период: ключ создан, но `set_not_new` не защищён — пользователь не видит ключ

**Где:** `src/novaaltairbot/handlers/user_handlers.py:65-81` (особенно `:77`)

**Симптом:** `new_key` прошёл, ключ создан в 3x-ui и БД, затем `await api.set_not_new(...)` падает (404/сеть/500) → исключение, сообщение с ключом не отправлено. Пользователь остаётся с `is_new=True` и без ключа на экране. Подтверждено локально (кейс F).

**Как чинить:** выдача ключа — главное; `set_not_new` — побочный эффект, он не должен ломать показ:

```python
new_key = await api.new_key(...)
try:
    await api.set_not_new(UserInUsername(username=username))
except ApiError:
    log.warning("set_not_new failed for %s", username)
# далее — всегда показываем ключ
```

Плюс поймать `XuiException` (500) и `DbAddException` (400) — сейчас ловится только `XuiNameException` (`:73`), любой другой ответ = падение.

---

## P0-5. `/start`: пароль отправляется **до** создания пользователя, `409` не обрабатывается

**Где:** `src/novaaltairbot/handlers/user_handlers.py:37-62`

**Симптом (два сценария):**
1. `get_user` → 404, бот сразу отправляет логин/пароль (`:55-56`), затем `new_user` (`:60`). Если создание упало (сеть/500/409) — у пользователя на руках пароль от несуществующего аккаунта, а бот молчит.
2. `TelegramIdAlreadyExists` не импортирован и не ловится нигде (проверено grep'ом) → необработанное исключение (подтверждено репро-кейсом A). Сейчас эта ветка почти недостижима (см. P0-6: `telegram_id` больше не отправляется), но код остаётся хрупким: как только идентификатор вернут — баг снова активен.

**Как чинить:** создавать/получать пользователя, и только **после** успеха — отправлять пароль; 409 обрабатывать отдельно.

```python
try:
    user = await api.get_user(username)
except UserNotFound:
    user = None

if user is None:
    password = secrets.token_urlsafe(12)
    try:
        user = await api.new_user(UserIn(
            username=username, password=password,
            referred_by_id=referred_id,
        ))
    except TelegramIdAlreadyExists:
        user = await api.get_user(username)
    else:
        await msg.answer(LEXICON["first_msg"].format(username=username, password=password),
                         parse_mode="HTML", reply_markup=get_agreement_kb())
```

Заодно: `password` генерируется в начале хендлера (`:43`) — то есть **всегда**, даже для существующего пользователя; генерируйте только в ветке создания.

---

## P0-6. Убрали `telegram_id` → реферальные ссылки на новых пользователей ломаются (FK → 500)

**Где:** `src/novaaltairbot/api/schemas.py:5-17` (в `UserIn`/`UserOut` больше нет `telegram_id`), `user_handlers.py:45-50` (ссылка `ref_` всё ещё парсится), `:59` (`referred_by_id` всё ещё отправляется) + API `models.py`/`db.py`.

**Что происходит:**
1. Бот больше не передаёт `telegram_id`, поэтому API создаёт `users` с `telegram_id = NULL` (в `UserIn` API поле опционально).
2. В API `referred_by_id` — это `ForeignKey("users.telegram_id")`, а в `db.py` включено `PRAGMA foreign_keys=ON`.
3. Все пользователи, созданные после этого изменения, имеют `telegram_id = NULL` (старые строки, если создавались с идентификатором, могут его сохранить) → вставка с `referred_by_id`, указывающим на такого нового пользователя, нарушает FK → `IntegrityError` → FastAPI 500 → бот получает generic `Exception` → `/start ref_<id>` падает, пользователь не создаётся.

То есть после этого коммита реферальная ссылка на любого **нового** пользователя — отказ регистрации. Плюс побочные эффекты:
- `409` в `POST /user/new` стал недостижим (`get_or_create_user` возвращает `None` только при существующем `telegram_id`);
- `GET /get/telegram_id/{telegram_id}` бесполезен;
- никто не может связать строку в БД с Telegram-аккаунтом (аналитика, админка, будущие наказания/баны);
- при смене схемы `user_<id>` появятся дубли одного человека (дедупликация была именно по `telegram_id`).

**Как решать (выбрать одно):**
- **A (рекомендую):** вернуть `telegram_id` в `UserIn`, отправлять его в `/user/new`, а `referred_by_id` проверять через `GET /get/telegram_id/{id}` (в клиенте этого метода нет — добавить) и запрещать self-referral;
- **B:** если `telegram_id` убрали осознанно — убрать и `referred_by_id` из запроса (иначе 500), а привязку к Telegram хранить отдельно.

---

# P1 — логические ошибки

## P1-1. «Назад» всегда рисует меню без кнопки пробного периода
**Где:** `user_handlers.py:34` → `get_main_kb(None)`.
`get_main_kb(None)` (`keyboards/inline.py:15-17`) — это ветка «не новый пользователь»: «Основная подписка» + «Продление». Новый пользователь, зашедший в «Профиль» и нажавший «Назад», теряет кнопку «Пробная подписка» и «Купить подписку» до повторного `/start`.
**Фикс:** `back_main_page` должен получать `api`, запрашивать `get_user` и передавать реального пользователя в `get_main_kb`.

## P1-2. «Купить подписку» исчезает навсегда после триала
**Где:** `keyboards/inline.py:9-14`, `user_handlers.py:116-120`.
Кнопка `buy_sub` есть только при `is_new == True`. После пробного периода остаются «Основная подписка» и «Продление», а `extend_sub` — заглушка. Купить платную подписку негде. Нужно решить продуктово: `buy_sub` показывать всегда, `extend_sub` — только при наличии ключа.

## P1-3. Пять функций с одним именем `extend_sub`; опечатка `relaod_sub`; мёртвые кнопки
**Где:** `user_handlers.py:123, 131, 137, 143, 150`.
Статический анализ: `{'extend_sub': 5}`. Обработчики регистрируются, но имя перезаписывается — отладка и трейсбеки врут, IDE не находит. Плюс:
- `relaod_sub` (`:143`, `keyboards/inline.py:34`) — опечатка, «согласованная» между клавиатурой и хендлером;
- кнопка «Инструкция» в профиле (`inline.py:45`) шлёт `get_instruction`, **обработчика нет** — кнопка не работает (проверено статически: `DEAD BUTTONS: ['get_instruction']`);
- «Инструкция» на экране подписки (`inline.py:33`) шлёт `get_connect_page` — не тот экран;
- «Подлючиться» (`inline.py:30`) — опечатка в тексте.

## P1-4. «Продление» показывает «Выберите тариф» **без тарифов**
**Где:** `user_handlers.py:123-127`.
`text = LEXICON["rate"]`, а клавиатура — `get_back_kb()` (только «Назад»). Пользователь видит заголовок «Выберите тариф» и одну кнопку «Назад». Должна быть `get_buy_rate_kb()` (как в `buy_sub`) либо честная заглушка.

## P1-5. Профиль: `@None` и `Payment id: None`
**Где:** `user_handlers.py:107, 111`; шаблон `lexicon.py:11-17`.
- `callback.from_user.username` бывает `None` (у многих пользователей нет @ника) → «🪪 @None»;
- `key.payment_id` отсутствует → `<pre>None</pre>`;
- в ветке `KeyNotFound` передаётся `expiry_time=None` → «Активна до **None**».

Подтверждено репро-кейсом: `... 🪪 @None ... Payment id: <pre>None</pre>`.
**Фикс:** `html.escape(callback.from_user.username or "—")`, `payment_id or "—"`, `expiry_time or "—"`.

## P1-6. Один жёсткий `email = sub_<telegram_id>` на всё
**Где:** `user_handlers.py:25-26, 90, 105`.
`get_key` ищет ключ только по `sub_<id>`. Любой платный ключ с другим `email` (API создаёт ключи по `email`, `Keys.email` unique) бот не найдёт — «У вас еще нет ключа». При этом в API есть `GET /user/keys/{username}` (список ключей) — его и надо использовать, а `email` формировать с типом подписки.

## P1-7. Время истечения показывается в UTC без пометки
**Где:** `user_handlers.py:79, 95, 111`.
API хранит `DateTime(timezone=True)` (UTC). `strftime('%Y-%m-%d %H:%M:%S')` печатает UTC-числа; пользователь в Москве видит время на 3 часа раньше. **Фикс:** `key.expiry_time.astimezone(ZoneInfo("Europe/Moscow")).strftime(...)` + TZ в конфиге.

## P1-8. Нет проверки «ключ истёк»
**Где:** `user_handlers.py:83-97`.
Просроченный ключ отображается как действующий, никакого «истекла, продлите» нет. **Фикс:** сравнение с `datetime.now(timezone.utc)` и отдельный текст/кнопка.

## P1-9. Любой 409 трактуется как «ты уже использовал пробный период»
**Где:** `user_handlers.py:73-75`.
409 приходит и при конфликте имени в 3x-ui (любом, не только триала), и при прочих конфликтах. Сообщение «Ах ты шалунишка» может быть ложным. **Фикс:** проверять `user.is_new`/наличие ключа до запроса, а 409 показывать нейтрально.

## P1-10. Динамические значения вставляются в HTML без экранирования
**Где:** `user_handlers.py:79, 95, 111`; `lexicon.py:3-9`.
`sub_link`, `username`, `payment_id` подставляются в `<code>`/`<pre>`/`<b>` как есть. Если в ссылке появится `&` (например, API начнёт отдавать `?token=...&...`) или `<` — Telegram ответит `ENTITY_TEXT_INVALID` / `can't parse entities`. В логе такие ошибки уже были (`ENTITY_TEXT_INVALID` на экране подписки, `Can't find end tag corresponding to start tag "b"` в профиле). Сейчас `sub_link` = `{xui_sub_base}/{sub_id}` без query, поэтому баг латентный, но стрельнёт при любом изменении ссылки.
**Фикс:** `from html import escape` для всех подстановок + fallback: при `TelegramBadRequest` отправить текст без `parse_mode`.

## P1-11. Стили кнопок и кастомные эмодзи — хрупкая зависимость от Bot API
**Где:** `keyboards/inline.py` (все `style=` и `icon_custom_emoji_id=`).
`style` появился в Bot API 9.2 (в клиентах — после 09.02.2026), `icon_custom_emoji_id` официально доступен ботам с купленным username на Fragment / Premium у владельца. В логе есть отказ сервера: `can't parse InlineKeyboardButton: Invalid button style specified` на экране подписки. Локально это не воспроизвести (валидирует сервер), поэтому нужно: (а) проверить, что бот имеет право на кастомные эмодзи, (б) добавить fallback — при `TelegramBadRequest` повторить отправку без `style`/`icon_custom_emoji_id`.

## P1-12. Конфиг без валидации: падение на старте и «странные» 422
**Где:** `config.py:4-12`.
Проверено локально:
- `FREE_TRIAL_DAYS=` (пусто) → `ValidationError: unable to parse string as an integer`;
- отсутствующая переменная → `Field required`;
- `extra="forbid"` (по умолчанию у pydantic-settings) → **любой лишний ключ в `.env`** (например `LOG_LEVEL=INFO`) = падение старта: `Extra inputs are not permitted`;
- `FREE_TRIAL_DAYS=400` принимается, а API ждёт `gt=0, le=365` → 422 → generic `Exception` → краш;
- `API_PATH=not-a-url` принимается как строка → падение уже в aiohttp;
- `bot` — обычная `str`, токен светится в repr/логах.

**Фикс:** `SecretStr`, `AnyHttpUrl`, `Field(ge=1, le=365)`, `extra="ignore"`, `env_file_encoding="utf-8"`, понятные сообщения об ошибке и `env_file=Path(__file__).parents[2] / ".env"`.

## P1-13. `UserOut.is_new` по умолчанию `True` маскирует отсутствие поля
**Где:** `schemas.py:17`.
Если API перестанет отдавать `is_new`, все пользователи окажутся «новыми» и увидят кнопку триала повторно. Лучше обязательное поле или `None` + явная обработка.

---

# P2 — надёжность, эксплуатация, безопасность

1. **Нет проверки токена на старте.** В логе 76 × `TelegramUnauthorizedError` — бот крутил polling с невалидным токеном. Нужно `await bot.get_me()` до polling и `sys.exit(1)` с внятным сообщением.
2. **Нет проверки прокси/API на старте.** В логе ~70 сетевых/прокси-ошибок (`ProxyConnectionError`, `ProxyTimeoutError`, `ServerDisconnected`). Нужен health-check `GET {api_path}/docs` и понятный лог; при желании — алерт.
3. **`drop_pending_updates`/`delete_webhook` не вызываются.** После простоя бот обработает старые апдейты (в т.ч. `/start`), а если на бота когда-то ставили webhook — polling упадёт с 409. Добавить `await bot.delete_webhook(drop_pending_updates=True)` и `drop_pending_updates=True` в `start_polling`.
4. **Относительные пути.** `assets/...` (`user_handlers.py:40`), `.env`, `bot.log` (`main.py:16`) зависят от CWD: запуск не из корня = `FileNotFoundError`; в Docker лог пишется в `/app/bot.log` и теряется при рестарте. Нужны пути от `Path(__file__)` и volume/`docker compose logs` без файла.
5. **Логирование.** `basicConfig` без `force=True`, без уровня из конфига, без логгера приложения (ни одного `getLogger(__name__)`) — в логах нет ни «создан пользователь», ни «выдан ключ», ни ID апдейта. Легко добавить `user_id` в `LogRecord` через filter/middleware. Плюс `logs/bot.log` (0 байт) намекает, что путь задумывался другим.
6. **Нет rate limiting / антифлуда.** Кнопки можно спамить (в т.ч. «пробная» и «купить»); нет блокировки повторных нажатий.
7. **Нет фильтра приватного чата.** `CommandStart()` сработает и в группе: бот создаст аккаунт любому, кто напишет `/start`. Добавить `F.chat.type == "private"` и `F.from_user`.
8. **Callback-хендлеры не проверяют регистрацию.** Кнопка из старого сообщения у незнакомого пользователя приведёт к `get_key` для несуществующего username → 404/500. Нужен middleware «получить/создать пользователя» для всех callback.
9. **Нет идемпотентности и защиты от двойного клика.** Двойное нажатие «Пробная» = два запроса (второй 409 — но пользователь видит «уже использовал»). Для будущего продления/оплаты это критично: нет `idempotency key`.
10. **Таймаут 10 с на всё** (`api.py:13`). `POST /user/key/add` включает логин в 3x-ui и добавление клиента — 10 с может не хватить; при таймауте ключ может уже создаться, а бот покажет ошибку. Нужны `connect=5, total=30` и отдельная обработка таймаута как «неизвестный результат».
11. **Нет ретраев.** Для GET-ов (`get_key`, `get_user`) безопасно добавить 1–2 повтора с backoff; для POST — нельзя без идемпотентности.
12. **`ContentTypeError`.** `await response.json()` вызывается без проверки `Content-Type` — если API вернул `text/plain` (500), получаем `ContentTypeError` (в логе есть). Брать `response.text()` и парсить `json.loads` с обработкой.
13. **URL-параметры не экранируются.** `f"/user/key/get/{email}"` (`api.py:59`) и `f"/get/username/{username}"` (`:68`) — `quote(email, safe="")`, иначе `/`, `?`, `#`, пробел ломают путь.
14. **`base_url` с путём молча теряет путь.** Проверено: `URL("http://host/api").join(URL("/user/new"))` → `http://host/user/new`. Если `API_PATH` когда-нибудь станет `http://host/api`, бот будет ходить не туда. Фикс: `API_PATH.rstrip("/")` + относительные пути без ведущего `/` или явная проверка.
15. **`self.session` — `Optional`, но используется без проверки** (`api.py:27,36,49,59,68`) → `AttributeError: 'NoneType'` при вызове вне `async with`.
16. **Star-imports** (`api.py:3-4`) — скрывают зависимости, конфликтуют имена, ломают линтинг.
17. **Дубли импорта `secrets`** (`user_handlers.py:4` и `:15`); неиспользуемые параметры `api` в 5 хендлерах; `UserIn(..., is_referral_rewarded=False)` — поле API не использует.
18. **Нет тестов.** `pytest` собирает 0 тестов → exit code 5; `uv run pytest` из README завершается «ошибкой». Оба теста в `tests/test_api.py` закомментированы и ходят в живой API. Нужны unit-тесты на клиент (мок aiohttp/`aiohttp.test_utils`) и хендлеры (фейковые Message/CallbackQuery), `conftest.py`, фикстуры.
19. **Нет линтера/типизации/CI.** Нет `ruff`, `mypy`, `pre-commit`, GitHub Actions. Текущий код содержит и дубли, и star-imports, и `Optional` без проверки — всё это ловится статикой.
20. **Docker/Compose.**
    - `COPY . .` до `uv sync` (`Dockerfile:10-12`) — кэш зависимостей убивается любой правкой кода; правильно: сначала `pyproject.toml` + `uv.lock`, `uv sync --frozen --no-install-project`, потом исходники;
    - контейнер работает от root, нет `HEALTHCHECK`, нет `init: true`, нет лимитов логов/`read_only`;
    - нет `TZ=Europe/Moscow` — логи и время расходятся;
    - в образ попадают неиспользуемые картинки (~2.5 МБ) и `README`;
    - нет тома для `bot.log` (а файл всё равно не нужен в контейнере).
21. **README расходится с кодом.** «Четыре запроса» — в клиенте пять; «`get_user` никому не понадобился» — он используется в `/start`; «тесты почти закомментированы» — они **полностью** закомментированы; `.env` в примере с пустым `FREE_TRIAL_DAYS` (а это падение старта); про `telegram_id`/рефералку README уже не соответствует коду. Документацию стоит синхронизировать.
22. **`pyproject.toml`.** `requires-python = ">=3.14"` — очень узко (CI/хостинг/образы часто без 3.14); опечатка в `description` («telgram»); нет `[project.scripts]`, `license`, `[tool.ruff]`, `[tool.mypy]`, `[tool.coverage]`.
23. **Секреты.** `.env` (реальный токен и прокси с логином/паролем) в рабочей папке; `.gitignore` его исключает — хорошо, но при передаче архива/папки он утечёт. Рекомендация: `SecretStr`, не печатать `settings`, при утечке — перевыпустить токен и сменить пароль прокси. `bot.log` содержит ID пользователей.
24. **Пустые модули и «заглушки».** `states/state.py` (0 байт), `handlers/payments.py` и `handlers/admin_handlers.py` — пустые роутеры; они включены в `main.py:26-27`, но ничего не делают. Либо реализовать, либо убрать.
25. **Нет обработки `TelegramForbiddenError`** (пользователь заблокировал бота) и `TelegramRetryAfter` (флуд-контроль). При рассылках/уведомлениях это обязательное.
26. **Нет i18n / единого источника текстов.** Часть текстов в `lexicon.py`, часть — хардкодом в хендлерах («Ах ты шалунишка…», «У вас еще нет ключа»).

---

# P3 — что нужно добавить (продукт и инфраструктура)

## Оплата и продление (сейчас нет вообще)
- `payments.py`: интеграция с провайдером (в истории коммитов фигурирует `rollypay`; варианты — Telegram Stars, ЮKassa, Robokassa, CryptoBot). Нужны: создание счёта, `pre_checkout_query`, `successful_payment`, идемпотентность по `payment_id`, возвраты, чек.
- `extend_sub`: `POST /user/key/extend` в API **уже есть** (`email`, `day_expiry`, `payment_id`) — клиенту не хватает метода, боту — FSM-сценария и оплаты.
- `relaod_sub` (перевыпуск): `POST /user/key/remove` + `POST /user/key/add` в API есть.
- Тарифы — вынести в данные/конфиг (`Tariff` с ценой, днями, провайдером), а не в тексты кнопок. Сейчас `keyboards/inline.py:62-65` хардкодит «99/179/359/539 руб/мес.» — и подписи выглядят противоречиво (179/мес за 2 месяца дороже 99/мес).
- FSM-хранилище (Redis) + `states/state.py` для сценариев оплаты/продления.

## Рефералка
- Вернуть/сохранить `telegram_id` (см. P0-6) — иначе механика невозможна.
- Начисление вознаграждения (`is_referral_rewarded` в API есть, логики нет), проверка существования реферера, запрет self-referral, статистика приглашённых, «Пригласить» с готовой ссылкой `https://t.me/<bot>?start=ref_<id>`.

## Подписка и инструкция
- «Подключиться»: страница с инструкциями под iOS/Android/Windows и deep-link на `sub_link` (сейчас — заглушка «plug»).
- «Инструкция»: реализовать `get_instruction` (кнопка уже есть, обработчика нет).
- Уведомления об истечении подписки (APScheduler/ARQ + `expiry_time`), напоминания за 3/1 день.
- Поддержка нескольких ключей на пользователя (`GET /user/keys/{username}`), разделение trial/paid.

## Админка
- `admin_handlers.py`: `/admin` с проверкой `admin_ids` из конфига; выдать/снять триал, посмотреть пользователя, перевыпустить ключ, статистика (регистрации, конверсия trial→paid), рассылка.

## Наблюдаемость и качество
- structlog/JSON-логи + request-id, Sentry/GlitchTip, метрики (счётчики регистраций/выдач/ошибок).
- GitHub Actions: `ruff check`, `ruff format --check`, `mypy`, `pytest --cov`; `pre-commit`.
- Тесты: unit на `api.py` (мок сессии), хендлеры (фейки), контрактные тесты на схемы API, e2e хотя бы на `/start` + «пробная».
- `Makefile`/`justfile`: `lint`, `test`, `run`, `docker`.

## Безопасность/приватность
- `SecretStr` для токена и ключа API; не логировать `settings`.
- Не хранить пароль в переписке дольше необходимого (кнопка «Удалить сообщение с паролем»).
- Ограничение частоты, проверка `chat.type`, `from_user.is_bot`.
- Политика конфиденциальности уже есть ссылкой, но нет явного шага согласия — решить юридически (кнопка «Принимаю» перед созданием аккаунта).

---

# План исправлений

**День 1 (P0, без продукта):**
1. `render()` с `edit_text`/`edit_caption` + `TelegramBadRequest` (P0-1).
2. `@dp.errors` + тексты ошибок (P0-2).
3. `ApiError`/`ApiUnavailable` + `_request` + таймауты (P0-3, P2-10, P2-12, P2-13).
4. Порядок «создать → отправить пароль», обработка 409 (P0-5).
5. `set_not_new` в `try` (P0-4).
6. Решение по `telegram_id` + проверка реферера (P0-6).

**Неделя 1 (P1 + надёжность):**
7. `back_main_page` с реальным пользователем; `buy_sub` всегда; «Продление» с тарифами (P1-1, P1-2, P1-4).
8. Переименовать дубли, починить/удалить мёртвые кнопки, опечатки (P1-3).
9. `html.escape`, `None`-значения, TZ, статус «истёк» (P1-5, P1-7, P1-8, P1-10).
10. Валидация конфига, `SecretStr`, пути от `__file__` (P1-12, P2-4).
11. `get_me` на старте, `delete_webhook`, `drop_pending_updates`, rate limit, private-only (P2-1..P2-8).

**Неделя 2 (качество и продукт):**
12. Тесты + CI + ruff/mypy (P2-18, P2-19).
13. Docker-харденинг (P2-20).
14. `payments.py` + `extend_sub` + тарифы (P3).
15. Рефералка, инструкция, уведомления, админка (P3).

---

# Проверено — это НЕ ошибки

Чтобы не тратить время на ложные срабатывания:

- **Сессия aiogram закрывается**: у `Dispatcher.start_polling` по умолчанию `close_bot_session=True` — отдельный `await bot.session.close()` не нужен.
- **Статусы API совпадают с клиентом**: `POST /user/new` → 201, `/user/key/add` → 201, `/user/set/not_new` → 201, `GET /user/key/get/{email}` → 200, `GET /get/username/{username}` → 200.
- **`X-API-Key` работает**: в API `security.verify_access` сравнивает ключ с `settings.bot_api_key` через `compare_digest` и пропускает бота без JWT.
- **Отсутствие `telegram_id` в запросе не даёт 422**: в API это поле опционально (`int | None = None`), поэтому запрос пройдёт — но с последствиями из P0-6.
- **`style` и `icon_custom_emoji_id` есть в aiogram 3.31** (поля `InlineKeyboardButton` присутствуют) — проблема не в библиотеке, а в поддержке на стороне Telegram (P1-11).
- **`compileall` проходит**, синтаксических ошибок нет.
- **`.env` не попадёт в git и в Docker-образ** (`.gitignore`, `.dockerignore`).
- **`aiohttp` с `base_url` без пути работает**; предупреждение только про `base_url` с путём (P2-14).

---

# Приложение: как воспроизводил

```powershell
# 1. Тесты
.\.venv\Scripts\python.exe -m pytest -q          # 0 tests, exit 5
.\.venv\Scripts\python.exe -m compileall -q src  # ok

# 2. Статика: дубли, мёртвые callback'и
python .tmp_audit\static_checks.py

# 3. Репро хендлеров (фейковые Message/CallbackQuery/API)
python .tmp_audit\repro_handlers.py

# 4. Разбор лога: 30 блоков трейсбеков, 318 ERROR/CRITICAL
python .tmp_audit\parse_log.py
```

Ключевые строки `bot.log`, на которые опирался:
`message text is empty` ×7 (back), `TelegramUnauthorizedError` ×76, `TelegramNetworkError` ×65, `ProxyConnectionError/TimeoutError`, `ContentTypeError` на `/user/new`, `ValidationError` (UserOut/UserIn), `ENTITY_TEXT_INVALID`, `Invalid button style specified`, `TypeError: main_keybord() missing 1 required positional argument`, `AttributeError: 'NoneType' object has no attribute 'is_new'`, `KeyError: 'sub'`.

---

# Хвосты

- Временные скрипты `.tmp_audit/` попали в коммит `7aa208e` вместе с вашими правками. Я удалил файлы с диска — в `git status` они висят как `deleted`. Достаточно закоммитить удаление (`git add -u .tmp_audit && git commit -m "drop temp audit scripts"`) или `git rm -r --cached .tmp_audit`.
- `bot.log` (277 КБ) не изменялся, только читался.
- Аудит написан по снимку `7aa208e`; если правите код параллельно — номера строк могут сместиться.
