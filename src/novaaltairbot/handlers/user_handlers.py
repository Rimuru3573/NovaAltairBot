from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from novaaltairbot.api.api import NeoForestlyApi
from novaaltairbot.api.schemas import (
    UserIn, UserOut
)
from neoforestlybot.lexicon import LEXICON
import secrets

router = Router()

@router.message(Command("start"))
async def start(msg: Message, api: NeoForestlyApi):
    text = LEXICON["start_msg"].format(name=msg.from_user.first_name)

    user = UserIn(msg.from_user.id, secrets.token_urlsafe(8), msg.from_user.id)
    await api.new_user(user)
    
    