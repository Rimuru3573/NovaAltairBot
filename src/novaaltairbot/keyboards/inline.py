from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton
from novaaltairbot.api.schemas import UserOut
from novaaltairbot.config import settings
from urllib.parse import quote

def get_main_kb(user: UserOut | None) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if user:
        if user.is_new == True:
            keyboard.row(InlineKeyboardButton(text="Пробная подписка", callback_data="get_free_sub", style="success", icon_custom_emoji_id="5429388216094444138"))
            keyboard.row(InlineKeyboardButton(text="Купить подписку", callback_data="buy_sub", style="primary", icon_custom_emoji_id="5260730055880876557"))
        else:
            keyboard.row(InlineKeyboardButton(text="Основная подписка", callback_data="get_my_sub", style="primary", icon_custom_emoji_id="5260730055880876557"))
            keyboard.row(InlineKeyboardButton(text="Продление", callback_data="extend_sub", style="primary", icon_custom_emoji_id="6005570495603282482"))
    else: 
        keyboard.row(InlineKeyboardButton(text="Основная подписка", callback_data="get_my_sub", style="primary", icon_custom_emoji_id="5260730055880876557"))
        keyboard.row(InlineKeyboardButton(text="Продление", callback_data="extend_sub", style="primary", icon_custom_emoji_id="6005570495603282482"))

    keyboard.row(InlineKeyboardButton(text="Пригласить", callback_data="referral_page", style="primary", icon_custom_emoji_id="6019363826024061450"))
    # keyboard.row(InlineKeyboardButton(text="Инструкция", callback_data="get_instruction", style="primary", icon_custom_emoji_id="5438151723199792420"),
                #  InlineKeyboardButton(text="Новости", url="https://t.me/мой_канал", style="primary", icon_custom_emoji_id="5877597667231534929"))
    keyboard.row(InlineKeyboardButton(text="Профиль", callback_data="get_profile", style="primary", icon_custom_emoji_id="5879770735999717115"),
                 InlineKeyboardButton(text="Поддержка", url="https://t.me/zxcurs4d", style="primary", icon_custom_emoji_id="5884510167986343350"))

    return keyboard.as_markup()

def get_my_sub_kb(sub_link: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" Подлючиться", callback_data="get_connect_page", style="primary", icon_custom_emoji_id="5260730055880876557"),
                 InlineKeyboardButton(text=" Продлить", callback_data="extend_sub", style="primary", icon_custom_emoji_id="5877410604225924969"))
    keyboard.row(InlineKeyboardButton(text=" Скопировать ссылку", copy_text=CopyTextButton(text=sub_link), style="primary"))
    keyboard.row(InlineKeyboardButton(text=" Инструкция", callback_data="instruction", style="primary", icon_custom_emoji_id="5992157823838984339"))
    keyboard.row(InlineKeyboardButton(text=" Перевыпустить", callback_data="relaod_sub", style="primary", icon_custom_emoji_id="5877410604225924969"))
    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()

def get_connect_kb(sub_link: str, email: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    encoded_sub = quote(sub_link, safe="")

    keyboard.row(InlineKeyboardButton(text="Happ", url=f"{settings.connect_path}/connect?client=happ&sub={encoded_sub}&email={email}", style="primary", icon_custom_emoji_id="5260730055880876557"),
                 InlineKeyboardButton(text="Incy", url=f"{settings.connect_path}/connect?client=incy&sub={encoded_sub}&email={email}", style="primary", icon_custom_emoji_id="5260730055880876557"))
    keyboard.row(InlineKeyboardButton(text="V2raytun", url=f"{settings.connect_path}/connect?client=v2raytun&sub={encoded_sub}&email={email}", style="primary", icon_custom_emoji_id="5260730055880876557"),
                 InlineKeyboardButton(text="V2rayng", url=f"{settings.connect_path}/connect?client=v2rayng&sub={encoded_sub}&email={email}", style="primary", icon_custom_emoji_id="5260730055880876557"))
    keyboard.row(InlineKeyboardButton(text="Hiddify", url=f"{settings.connect_path}/connect?client=hiddify&sub={encoded_sub}&email={email}", style="primary", icon_custom_emoji_id="5260730055880876557"),
                 InlineKeyboardButton(text="Singbox", url=f"{settings.connect_path}/connect?client=singbox&sub={encoded_sub}&email={email}", style="primary", icon_custom_emoji_id="5260730055880876557"))
    keyboard.row(InlineKeyboardButton(text=" Инструкция", callback_data="instruction", style="primary", icon_custom_emoji_id="5992157823838984339"))
    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="get_my_sub", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()

def get_instruction_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" iPhone & iPad", url="https://apps.apple.com/app/happ-proxy-utility/id6504287215", style="primary", icon_custom_emoji_id="5818920837645867167"))
    keyboard.row(InlineKeyboardButton(text=" Android", url="https://play.google.com/store/apps/details?id=com.happproxy", style="primary", icon_custom_emoji_id="5226673499254332561"))
    keyboard.row(InlineKeyboardButton(text=" Windows", url="https://happ.su/?", style="primary", icon_custom_emoji_id="5366318141771096216"))
    keyboard.row(InlineKeyboardButton(text=" Linux", url="https://happ.su/?", style="primary", icon_custom_emoji_id="5319153460921251668"))
    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="get_connect_page", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()


def get_profile_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" Соглашение", url="https://telegra.ph/Polzovatelskoe-soglashenie-servisa-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"),
                 InlineKeyboardButton(text=" Политика", url="https://telegra.ph/Politika-v-otnoshenii-obrabotki-personalnyh-dannyh-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"))
    keyboard.row(InlineKeyboardButton(text=" Инструкция", callback_data="get_instruction", style="primary", icon_custom_emoji_id="5992157823838984339"))
    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()

def get_agreement_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" Соглашение", url="https://telegra.ph/Polzovatelskoe-soglashenie-servisa-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"),
                InlineKeyboardButton(text=" Политика", url="https://telegra.ph/Politika-v-otnoshenii-obrabotki-personalnyh-dannyh-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"))

    return keyboard.as_markup()


def get_buy_rate_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    # Заглушка в виде колбюек даты
    keyboard.row(InlineKeyboardButton(text="1 мес. - 99  руб.", callback_data="plug", style="primary", icon_custom_emoji_id="5231449120635370684"))
    keyboard.row(InlineKeyboardButton(text="2 мес. - 179 руб.", callback_data="plug", style="primary", icon_custom_emoji_id="5231449120635370684"))
    keyboard.row(InlineKeyboardButton(text="4 мес. - 359 руб.", callback_data="plug", style="primary", icon_custom_emoji_id="5231449120635370684"))
    keyboard.row(InlineKeyboardButton(text="6 мес. - 539 руб.", callback_data="plug", style="primary", icon_custom_emoji_id="5231449120635370684"))
    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()



def get_back_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()