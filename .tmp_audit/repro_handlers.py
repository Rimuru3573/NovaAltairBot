"""Reproduce handler-level failures without Telegram or the real API."""

import asyncio
import sys
import types

sys.path.insert(0, "src")

from novaaltairbot.errors import TelegramIdAlreadyExists, UserNotFound
from novaaltairbot.handlers import user_handlers as uh


class FakeMessage:
    def __init__(self, text_caption: bool = True):
        self.from_user = types.SimpleNamespace(id=555, username="no_username_here")
        self.caption = "x" if text_caption else None
        self.chat = types.SimpleNamespace(id=555)
        self.sent: list[dict] = []

    async def answer(self, text=None, **kw):
        self.sent.append(("answer", text, kw))
        return self

    async def answer_photo(self, photo=None, **kw):
        self.sent.append(("answer_photo", kw))
        return self

    async def edit_caption(self, **kw):
        if self.caption is None:
            raise RuntimeError("TelegramBadRequest: Bad Request: message text is empty")
        self.sent.append(("edit_caption", kw))
        return self

    async def edit_text(self, **kw):
        self.sent.append(("edit_text", kw))
        return self


class FakeCallback:
    def __init__(self, message, data):
        self.from_user = types.SimpleNamespace(id=555, username=None)
        self.message = message
        self.data = data
        self.answered = False

    async def answer(self, *a, **kw):
        self.answered = True


class FakeApi:
    def __init__(self, existing_user=False, create_error=None, not_new_error=None, key=None):
        self.existing_user = existing_user
        self.create_error = create_error
        self.not_new_error = not_new_error
        self.key = key
        self.calls: list[str] = []

    async def get_user(self, username):
        self.calls.append("get_user")
        if not self.existing_user:
            raise UserNotFound()
        from novaaltairbot.api.schemas import UserOut

        return UserOut(id=1, username=username, telegram_id=555, is_new=False)

    async def new_user(self, user):
        self.calls.append("new_user")
        if self.create_error:
            raise self.create_error
        from novaaltairbot.api.schemas import UserOut

        return UserOut(id=1, username=user.username, telegram_id=555, is_new=True)

    async def new_key(self, payload):
        self.calls.append("new_key")
        if self.key is None:
            raise AssertionError("not used here")
        return self.key

    async def get_key(self, email):
        self.calls.append("get_key")
        if self.key is None:
            from novaaltairbot.errors import KeyNotFound

            raise KeyNotFound()
        return self.key

    async def set_not_new(self, payload):
        self.calls.append("set_not_new")
        if self.not_new_error:
            raise self.not_new_error


async def case(title, coro):
    print(f"\n--- {title} ---")
    try:
        await coro
        print("OK (no exception)")
    except Exception as exc:  # noqa: BLE001
        print(f"CRASH: {type(exc).__name__}: {exc}")


async def main():
    command = types.SimpleNamespace(args=None)

    await case(
        "A. /start for an EXISTING user (get_user OK, new_user -> 409)",
        uh.start(FakeMessage(), command, FakeApi(existing_user=True, create_error=TelegramIdAlreadyExists())),
    )

    await case(
        "B. /start when API is down (aiohttp error instead of domain error)",
        uh.start(FakeMessage(), command, FakeApi(existing_user=False, create_error=ConnectionError("API down"))),
    )

    await case(
        "C. /start first-time user (happy path)",
        uh.start(FakeMessage(), command, FakeApi(existing_user=False)),
    )

    await case(
        "D. 'back to main menu' pressed on a TEXT message (no caption)",
        uh.back_main_page(FakeCallback(FakeMessage(text_caption=False), "back_main_page")),
    )

    await case(
        "E. 'back to main menu' pressed on a PHOTO message (caption)",
        uh.back_main_page(FakeCallback(FakeMessage(text_caption=True), "back_main_page")),
    )

    from datetime import datetime, timezone

    from novaaltairbot.api.schemas import Key

    key_with_payment = Key(
        user_username="user_555",
        email="sub_555",
        sub_id="abc",
        sub_link="https://vpn.example.com/sub/abc?token=deadbeef&mode=auto",
        expiry_time=datetime(2027, 1, 1, 12, 0, tzinfo=timezone.utc),
        payment_id=None,
    )
    key_without_payment = key_with_payment.model_copy(update={"payment_id": "pay-1"})

    await case(
        "F. free trial: key created, but set_not_new -> 404 (user vanished)",
        uh.get_free_sub(
            FakeCallback(FakeMessage(), "get_free_sub"),
            FakeApi(key=key_without_payment, not_new_error=UserNotFound()),
        ),
    )

    await case(
        "G. 'get free sub' pressed on a TEXT message (no caption to edit)",
        uh.get_free_sub(
            FakeCallback(FakeMessage(text_caption=False), "get_free_sub"),
            FakeApi(key=key_without_payment),
        ),
    )

    await case(
        "H. profile for a user without @username and without payment_id",
        uh.get_profile(FakeCallback(FakeMessage(), "get_profile"), FakeApi(key=key_with_payment)),
    )

    msg = FakeMessage()
    await case(
        "I. profile: rendered text",
        uh.get_profile(FakeCallback(msg, "get_profile"), FakeApi(key=key_with_payment)),
    )
    print("   rendered:", repr(msg.sent[-1][1]["caption"]))

    msg2 = FakeMessage()
    await case(
        "J. subscription page with a real-looking sub_link (note raw '&' inside <code>)",
        uh.get_main_sub(FakeCallback(msg2, "get_my_sub"), FakeApi(key=key_with_payment)),
    )
    print("   rendered:", repr(msg2.sent[-1][1]["caption"]))

    await case(
        "K. subscription page on a TEXT message",
        uh.get_main_sub(FakeCallback(FakeMessage(text_caption=False), "get_my_sub"), FakeApi(key=key_with_payment)),
    )


asyncio.run(main())
