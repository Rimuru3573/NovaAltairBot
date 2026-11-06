from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, FSInputFile, CallbackQuery, LinkPreviewOptions
import secrets
from novaaltairbot.api.api import NovaAltairApi
from novaaltairbot.api.schemas import (
    UserIn, NewKeyIn, UserInUsername
)
from novaaltairbot.keyboards.inline import (
    get_my_sub_kb, get_profile_kb, get_agreement_kb, get_back_kb, get_buy_rate_kb, get_main_kb
)
from novaaltairbot.errors import UserNotFound, XuiNameException, KeyNotFound
from novaaltairbot.config import settings
from novaaltairbot.lexicon import LEXICON
import secrets



router = Router()


def get_username(telegram_id: int) -> str:
    return f"user_{telegram_id}"

def get_email(telegram_id: int) -> str:
    return f"sub_{telegram_id}"


@router.callback_query(F.data == "back_main_page")
async def back_main_page(callback: CallbackQuery):
    await callback.answer()
    text = LEXICON["start_msg"]

    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_main_kb(None))


@router.message(CommandStart())
async def start(msg: Message, command: CommandObject, api: NovaAltairApi):
    text = LEXICON["start_msg"]
    main_page = FSInputFile("./assets/Altair_main_page_v4.jpg")
    telegram_id = msg.from_user.id
    username = get_username(telegram_id)
    password = str(secrets.token_urlsafe(8))

    referred_id = None
    if command.args and command.args.startswith("ref_"):
        try:
            referred_id = int(command.args.replace("ref_", ""))
        except ValueError:
            pass

    try:
        user = await api.get_user(username)
    except UserNotFound:
        txt = LEXICON["first_msg"].format(username=username, password=password)
        await msg.answer(txt, parse_mode="HTML", reply_markup=get_agreement_kb())


    user = UserIn(username=username, password=password, referred_by_id=referred_id)
    db_user = await api.new_user(user)

    await msg.answer_photo(photo=main_page, caption=text, parse_mode="HTML", reply_markup=get_main_kb(db_user))


@router.callback_query(F.data == "get_free_sub")
async def get_free_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    username = get_username(callback.from_user.id)
    email = get_email(callback.from_user.id)

    try:
        new_key = await api.new_key(NewKeyIn(username=username, email=email, day_expiry=settings.free_trial_days, payment_id=None))
    except XuiNameException:
        await callback.message.answer(text="Ах ты шалунишка, ты уже использовал пробный период!", parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=get_back_kb())
        return

    await api.set_not_new(UserInUsername(username=username))
    sub_link = new_key.sub_link
    text = LEXICON["main_sub"].format(sub=sub_link, expiry_time=new_key.expiry_time.strftime('%Y-%m-%d %H:%M:%S'), username=username)

    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_my_sub_kb(sub_link))

@router.callback_query(F.data == "get_my_sub")
async def get_main_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    username = get_username(callback.from_user.id)
    email = get_email(callback.from_user.id)

    try:
        key = await api.get_key(email=email)
    except KeyNotFound:
        await callback.message.edit_caption(caption="У вас еще нет ключа", reply_markup=get_back_kb())
        return

    text = LEXICON["main_sub"].format(sub=key.sub_link, expiry_time=key.expiry_time.strftime('%Y-%m-%d %H:%M:%S'), username=username)

    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_my_sub_kb(key.sub_link))


@router.callback_query(F.data == "get_profile")
async def get_profile(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    username = get_username(callback.from_user.id)
    try:
        key = await api.get_key(get_email(callback.from_user.id))
    except KeyNotFound:
        text = LEXICON["profile"].format(name=callback.from_user.username, username=username, expiry_time=None, payment_id=None)
        await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_profile_kb())
        return
    
    text = LEXICON["profile"].format(name=callback.from_user.username, username=username, expiry_time=key.expiry_time.strftime('%Y-%m-%d %H:%M:%S'), payment_id=key.payment_id)

    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_profile_kb())


@router.callback_query(F.data == "buy_sub")
async def buy_sub(callback: CallbackQuery):
    await callback.answer()
    text = LEXICON["rate"]
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_buy_rate_kb())


@router.callback_query(F.data == "extend_sub")
async def extend_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    text = LEXICON["rate"]
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_back_kb())



@router.callback_query(F.data == "referral_page")
async def extend_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    text = LEXICON["plug"]
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_back_kb())

@router.callback_query(F.data == "get_connect_page")
async def extend_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    text = LEXICON["plug"]
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_back_kb())

@router.callback_query(F.data == "relaod_sub")
async def extend_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    text = LEXICON["plug"]
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_back_kb())


@router.callback_query(F.data == "plug")
async def extend_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    text = LEXICON["plug"]
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_back_kb())