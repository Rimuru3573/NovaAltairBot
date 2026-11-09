from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, FSInputFile, CallbackQuery
import logging as log
import secrets
from novaaltairbot.api.api import NovaAltairApi
from novaaltairbot.api.schemas import (
    UserIn, NewKeyIn, UserInUsername
)
from novaaltairbot.keyboards.inline import (
    get_my_sub_kb, get_profile_kb, get_agreement_kb, get_back_kb, get_main_kb, get_connect_kb, get_instruction_kb, get_referral_kb
)
from novaaltairbot.errors import UserNotFound, KeyNotFound
from novaaltairbot.config import settings
from novaaltairbot.lexicon import LEXICON, get_profile
import secrets


router = Router()


def get_username(telegram_id: int) -> str:
    return f"user_{telegram_id}"

def get_email(telegram_id: int) -> str:
    return f"sub_{telegram_id}"


@router.callback_query(F.data == "back_main_page")
async def back_main_page(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    text = LEXICON["start_msg"]

    user = await api.get_user(get_username(callback.from_user.id))
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_main_kb(user))


@router.message(CommandStart())
async def start(msg: Message, command: CommandObject, api: NovaAltairApi):
    text = LEXICON["start_msg"]
    main_page = FSInputFile("./assets/Altair_main_page_v4.jpg")
    telegram_id = msg.from_user.id
    username = get_username(telegram_id)
    password = str(secrets.token_urlsafe(8))
    referred_user = None
    if command.args and command.args.startswith("ref_"):
        referred_user = command.args.replace("ref_", "")

    try:
        user = await api.get_user(username)
    except UserNotFound:
        txt = LEXICON["first_msg"].format(username=username, password=password)
        await msg.answer(txt, parse_mode="HTML", reply_markup=get_agreement_kb())
    user = UserIn(username=username, password=password, referred_by_user=referred_user)
    db_user = await api.new_user(user)


    await msg.answer_photo(photo=main_page, caption=text, parse_mode="HTML", reply_markup=get_main_kb(db_user))


@router.callback_query(F.data == "get_free_sub")
async def get_free_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    username = get_username(callback.from_user.id)
    email = get_email(callback.from_user.id)
    new_key = await api.new_key(NewKeyIn(username=username, email=email, day_expiry=settings.free_trial_days, payment_id=None, limit_hwid=5))
    await api.set_not_new(UserInUsername(username=username))
    sub_link = new_key.sub_link


    text = LEXICON["main_sub"].format(sub=sub_link, expiry_time=new_key.expiry_time.strftime('%Y-%m-%d %H:%M:%S'), username=username)
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_my_sub_kb(sub_link))


@router.callback_query(F.data == "get_my_sub")
async def get_main_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    username = get_username(callback.from_user.id)
    email = get_email(callback.from_user.id)
    key = await api.get_key(email=email)

    text = LEXICON["main_sub"].format(sub=key.sub_link, expiry_time=key.expiry_time.strftime('%Y-%m-%d %H:%M:%S'), username=username)
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_my_sub_kb(key.sub_link))


@router.callback_query(F.data == "get_profile")
async def get_profile_(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    username = get_username(callback.from_user.id)
    referrals = await api.get_referrals_all(username)
    try:
        key = await api.get_key(get_email(callback.from_user.id))
    except KeyNotFound:
        pass

    text = get_profile(name=callback.from_user.username, username=username, expiry_time=key.expiry_time.strftime('%Y-%m-%d %H:%M:%S'), referrals=referrals, payment_id=key.payment_id)
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_profile_kb())

@router.callback_query(F.data == "instruction")
async def extend_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    text = LEXICON["instruction"]

    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_instruction_kb())


@router.callback_query(F.data == "get_connect_page")
async def extend_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    text = LEXICON["get_connect"]
    email = get_email(callback.from_user.id)

    key = await api.get_key(email=email)
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_connect_kb(sub_link=key.sub_link, email=email))


@router.callback_query(F.data == "relaod_sub")
async def extend_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    email = get_email(callback.from_user.id)
    old_key = await api.get_key(email)
    key = await api.reload_key(NewKeyIn(username=old_key.user_username, email=email, day_expiry=1, payment_id=old_key.payment_id))

    text = LEXICON["main_sub"].format(sub=key.sub_link, expiry_time=key.expiry_time.strftime('%Y-%m-%d %H:%M:%S'), username=old_key.user_username)
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_my_sub_kb(key.sub_link))


@router.callback_query(F.data == "referral_page")
async def referral_page(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    username = get_username(callback.from_user.id)
    referrals = await api.get_referrals(username)
    link = f"https://t.me/novaaltairbot?start=ref_{username}"

    text = LEXICON["referral_page"].format(referrals=referrals, days=(referrals * settings.referrals_day), referrals_day=settings.referrals_day, link=link)
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_referral_kb(link, referrals))


@router.callback_query(F.data == "free_extend")
async def free_extend(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    username = get_username(callback.from_user.id)
    email = get_email(callback.from_user.id)
    key = await api.get_key(email=email)
    referrals = await api.get_referrals(username)
    if referrals == 0:
        text = LEXICON["referral_0"]
        await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_back_kb())
    new_key = await api.referrals_reward(NewKeyIn(username=username, email=email, day_expiry=(referrals * settings.referrals_day), payment_id=key.payment_id))

    text = LEXICON["main_sub"].format(sub=new_key.sub_link, expiry_time=new_key.expiry_time.strftime('%Y-%m-%d %H:%M:%S'), username=username)
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_my_sub_kb(new_key.sub_link))



@router.callback_query(F.data == "plug")
async def extend_sub(callback: CallbackQuery, api: NovaAltairApi):
    await callback.answer()
    text = LEXICON["plug"]
    await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_back_kb())