import logging as log
import traceback
from aiogram import F, Router
from aiogram.types import ErrorEvent, Message, CallbackQuery
from aiogram.filters import ExceptionTypeFilter, ExceptionMessageFilter
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

root = Router(name="root_router")

class CustomException(Exception):
    pass

class TelegramIdAlreadyExists(Exception):
    pass

class XuiException(Exception):
    pass

class XuiNameException(Exception):
    pass

class DbAddException(Exception):
    pass

class UserNotFound(Exception):
    pass

class KeyNotFound(Exception):
    pass



@root.error(ExceptionTypeFilter(TelegramBadRequest), ExceptionMessageFilter("message is not modified"))
async def ignore_message_not_modified(event: ErrorEvent):
    log.debug("Попытка изменить сообщение на идентичное проигнорировано.")
    return True

@root.error(ExceptionTypeFilter(TelegramRetryAfter))
async def handle_retry_after(event: ErrorEvent):
    log.warning(f"Превышен лимит запросов. Нужно подождать {event.exception.retry_after} сек.")


@root.error(ExceptionTypeFilter(CustomException), F.update.message.as_("message"))
async def handle_db_error(event: ErrorEvent, message: Message):
    log.error(f"Ошибка в дб и/или xui: user_{message.from_user.id}: {event.exception}")
    await message.answer("Апи временно недоступно. Попробуйте через пару минут.")





@root.error()
async def global_error_handler(event: ErrorEvent):
    log.critical("Необработанное исключение: %s", event.exception, exc_info=True)

    update = event.update
    if update.message:
        await update.message.answer("Произошла непредвиденная ошибка. Мы уже чиним!")
    elif update.callback_query:
        await update.callback_query.answer(
            "Ошибка при выполнении действия.", show_alert=True
        )