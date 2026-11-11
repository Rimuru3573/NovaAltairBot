from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton
from novaaltairbot.api.schemas import UserOut
from novaaltairbot.config import settings
from urllib.parse import quote
from novaaltairbot.lexicon import LEXICON
from novaaltairbot.config import load_pricing


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
    keyboard.row(InlineKeyboardButton(text="Профиль", callback_data="get_profile", style="primary", icon_custom_emoji_id="5879770735999717115"),
                 InlineKeyboardButton(text="Поддержка", url="https://t.me/zxcurs4d", style="primary", icon_custom_emoji_id="5884510167986343350"))

    return keyboard.as_markup()

def get_my_sub_kb(sub_link: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" Подлючиться", callback_data="get_connect_page", style="primary", icon_custom_emoji_id="5260730055880876557"),
                 InlineKeyboardButton(text=" Продлить", callback_data="extend_sub", style="primary", icon_custom_emoji_id="5877410604225924969"))
    keyboard.row(InlineKeyboardButton(text=" Скопировать ссылку", copy_text=CopyTextButton(text=sub_link), style="primary"))
    keyboard.row(InlineKeyboardButton(text=" Устройства", callback_data="devices", style="primary", icon_custom_emoji_id="5258508428212445001"))
    keyboard.row(InlineKeyboardButton(text=" Перевыпустить", callback_data="reload_sub", style="primary", icon_custom_emoji_id="5877410604225924969"))
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
    keyboard.row(InlineKeyboardButton(text=" Подлючиться", callback_data="get_connect_page", style="primary", icon_custom_emoji_id="5260730055880876557"))
    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="get_connect_page", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()


def get_profile_kb(telegram_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if telegram_id in settings.admin_id:
        keyboard.row(InlineKeyboardButton(text="Админ панель", callback_data="admin_panel", style="success"))

    keyboard.row(InlineKeyboardButton(text=" Соглашение", url="https://telegra.ph/Polzovatelskoe-soglashenie-servisa-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"),
                 InlineKeyboardButton(text=" Политика", url="https://telegra.ph/Politika-v-otnoshenii-obrabotki-personalnyh-dannyh-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"))
    keyboard.row(InlineKeyboardButton(text=" Новости", url="https://t.me/мой_канал", style="primary", icon_custom_emoji_id="5877597667231534929"))

    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page", style="danger", icon_custom_emoji_id="5229079956545377277"))


    
    return keyboard.as_markup()

def get_agreement_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" Соглашение", url="https://telegra.ph/Polzovatelskoe-soglashenie-servisa-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"),
                InlineKeyboardButton(text=" Политика", url="https://telegra.ph/Politika-v-otnoshenii-obrabotki-personalnyh-dannyh-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"))

    return keyboard.as_markup()


# TODO: добавить отдельную клавиатуру с продлением и покупкой, в колбек дате указать типа f"extend_days_{price.months}"
def get_rate_kb(flag: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    pricing = load_pricing()

    keyboard.row(InlineKeyboardButton(text=f"{pricing.limitHwid} устройств.", callback_data="plug", style="success", icon_custom_emoji_id="5258508428212445001"))
    # flag - buy | extend
    for price in pricing.plans:
        keyboard.row(InlineKeyboardButton(text=f"{price.title} - {price.price} {pricing.currency}.", callback_data=f"{flag}_{price.months}", style="primary", icon_custom_emoji_id="5226723995184830803"))
    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page", style="danger", icon_custom_emoji_id="5229079956545377277"))


    return keyboard.as_markup()

def get_referral_kb(link: str, rederrals: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    text = LEXICON["referral_kb"]
    url = f"https://t.me/share/url?url={quote(link)}&text={quote(text)}"

    keyboard.row(InlineKeyboardButton(text=f" Использовать +{rederrals*settings.referrals_day} дней", callback_data="free_extend", style="primary", icon_custom_emoji_id="5260730055880876557"))
    keyboard.row(InlineKeyboardButton(text=" Пригласить", url=url, style="primary", icon_custom_emoji_id="5260730055880876557"))
    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()


def get_devices_kb(devices: list[str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for device in devices:
        id = int(device[0]) - 1
        keyboard.row(InlineKeyboardButton(text=device, callback_data=f"device", style="primary"))
    keyboard.row(InlineKeyboardButton(text=" Перевыпустить", callback_data="reload_sub", style="primary", icon_custom_emoji_id="5877410604225924969"))
    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="get_my_sub", style="danger", icon_custom_emoji_id="5229079956545377277"))
    return keyboard.as_markup()

# def get_device_kb(id: int) -> InlineKeyboardMarkup:
#     keyboard = InlineKeyboardBuilder()

#     keyboard.row(InlineKeyboardButton(text="Удалить устройство", callback_data=f"delete_hwid_{id}", style="primary", icon_custom_emoji_id="5807651380332076999"))
#     keyboard.row(InlineKeyboardButton(text=" Перевыпустить", callback_data="reload_sub", style="primary", icon_custom_emoji_id="5877410604225924969"))
#     keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="devices", style="danger", icon_custom_emoji_id="5229079956545377277"))

#     return keyboard.as_markup()


def get_back_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()