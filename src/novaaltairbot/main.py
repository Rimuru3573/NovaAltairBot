import asyncio
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher
from novaaltairbot.config import settings
from novaaltairbot.handlers import user_handlers, admin_handlers, payments
from novaaltairbot.api.api import NovaAltairApi
from logging.handlers import RotatingFileHandler
import logging as log
from novaaltairbot.errors import root

async def main():
    session = AiohttpSession(proxy=settings.proxy) if settings.proxy else None
    bot = Bot(settings.bot, session=session)
    dp = Dispatcher()

    log.basicConfig(
    level=log.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        log.StreamHandler(),
        RotatingFileHandler("logs/bot.log", maxBytes=5_000_000, backupCount=3, encoding="utf-16"),
        ],
    )

    root.include_routers(user_handlers.router, admin_handlers.router, payments.router)
    dp.include_router(root)

    async with NovaAltairApi(api_path=settings.api_path, bot_api_key=settings.bot_api_key) as api:
        log.info("Р‘РѕС‚ Р·Р°РїСѓС‰РµРЅ")
        await dp.start_polling(bot, api=api)
    



if __name__ == "__main__":
    asyncio.run(main())
