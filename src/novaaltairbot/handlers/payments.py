from aiogram import F, Router
from aiogram.types import CallbackQuery
from novaaltairbot.api.api import NovaAltairApi
from novaaltairbot.keyboards.inline import get_rate_kb
from novaaltairbot.lexicon import LEXICON


router = Router()


@router.callback_query(F.data == "buy_sub")
async def buy_sub(callback: CallbackQuery):
    await callback.answer()
    text = LEXICON["rate"]
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_rate_kb("buy"))


@router.callback_query(F.data == "extend_sub")
async def extend_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    text = LEXICON["rate"]
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_rate_kb("extend"))

