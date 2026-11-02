from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, FSInputFile
from novaaltairbot.keyboards.inline import *
from novaaltairbot.api.api import NovaAltairApi
from novaaltairbot.api.schemas import (
    UserIn
)
from novaaltairbot.lexicon import LEXICON
import secrets

router = Router()

@router.message(CommandStart)
async def start(msg: Message, command: CommandObject, api: NovaAltairApi):
    text = LEXICON["start_msg"]
    main_page = FSInputFile("./assets/Altair_main_page.jpg")

    try:
        user = UserIn(username=str(msg.from_user.id), password=str(secrets.token_urlsafe(8)), telegram_id=msg.from_user.id, referred_by_id=int(command.args))
    except ValueError:
        user = UserIn(username=str(msg.from_user.id), password=str(secrets.token_urlsafe(8)), telegram_id=msg.from_user.id, referred_by_id=0)

    await api.new_user(user)
    await msg.answer_photo(main_page, caption=text, parse_mode="Markdown", reply_markup=main_keybord(user))

    