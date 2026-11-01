import asyncio
from aiogram import Bot, Dispatcher
from novaaltairbot.config import settings
from novaaltairbot.handlers import user_handlers, admin_handlers, payments
from novaaltairbot.api.api import NeoForestlyApi

async def main():
    bot = Bot(settings.bot)
    dp = Dispatcher()

    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(payments.router)


    async with NeoForestlyApi(api_path=settings.api_path, bot_api_key=settings.bot_api_key) as api:
        await dp.start_polling(bot, api=api)



if __name__ == "__main__":
    asyncio.run(main())