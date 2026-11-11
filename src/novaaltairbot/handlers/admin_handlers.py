from aiogram import Router, F
from aiogram.types import CallbackQuery
from novaaltairbot.api.api import NovaAltairApi
from novaaltairbot.config import settings

router = Router()
router.message.filter(F.from_user.id.in_(settings.admin_id))
router.callback_query.filter(F.from_user.id.in_(settings.admin_id))

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    await callback.message.answer(text="Вы вошли в админ панель!")