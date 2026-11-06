from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton
from novaaltairbot.api.schemas import UserOut

# def main_keybord(user: UserOut | None) -> InlineKeyboardMarkup:
#     keyboard = InlineKeyboardBuilder()
#     if user:
#         if user.is_new == True:
#             keyboard.row(InlineKeyboardButton(text="Пробная подписка", callback_data="get_free_sub", style="success", icon_custom_emoji_id="5429388216094444138"))
#         else:
#             keyboard.row(InlineKeyboardButton(text="Основная подписка", callback_data="get_my_sub", style="primary", icon_custom_emoji_id="5260730055880876557"))
#     else: keyboard.row(InlineKeyboardButton(text="Основная подписка", callback_data="get_my_sub", style="primary", icon_custom_emoji_id="5260730055880876557"))
#     keyboard.row(InlineKeyboardButton(text="Продление", callback_data="extend_sub", style="primary", icon_custom_emoji_id="6005570495603282482"))
#     keyboard.row(InlineKeyboardButton(text="FAQ", callback_data="get_instruction", style="primary", icon_custom_emoji_id="5438151723199792420"),
#                  InlineKeyboardButton(text="Invite", callback_data="new_friend_page", style="primary", icon_custom_emoji_id="6019363826024061450"),
#                  InlineKeyboardButton(text="News", url="https://t.me/мой_канал", style="primary", icon_custom_emoji_id="5877597667231534929"))
#     keyboard.row(InlineKeyboardButton(text="Profile", callback_data="get_profile", style="primary", icon_custom_emoji_id="5879770735999717115"),
#                  InlineKeyboardButton(text="Support", url="https://t.me/zxcurs4d", style="primary", icon_custom_emoji_id="5884510167986343350"))

#     return keyboard.as_markup()

def main_keybord(user: UserOut | None) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if user:
        if user.is_new == True:
            keyboard.row(InlineKeyboardButton(text="Пробная подписка", callback_data="get_free_sub", style="success", icon_custom_emoji_id="5429388216094444138"))
        else:
            keyboard.row(InlineKeyboardButton(text="Основная подписка", callback_data="get_my_sub", style="primary", icon_custom_emoji_id="5260730055880876557"))
    else: keyboard.row(InlineKeyboardButton(text="Основная подписка", callback_data="get_my_sub", style="primary", icon_custom_emoji_id="5260730055880876557"))
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
    keyboard.row(InlineKeyboardButton(text=" Кнопка для вида", callback_data="get_connect_page", style="primary", icon_custom_emoji_id="5260730055880876557"))
    keyboard.row(InlineKeyboardButton(text=" Перевыпустить", callback_data="relaod_sub", style="primary", icon_custom_emoji_id="5877410604225924969"))
    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page_photo", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()


def get_profile_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" Соглашение", url="https://telegra.ph/Polzovatelskoe-soglashenie-servisa-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"),
                 InlineKeyboardButton(text=" Политика", url="https://telegra.ph/Politika-v-otnoshenii-obrabotki-personalnyh-dannyh-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"))
    keyboard.row(InlineKeyboardButton(text=" Инструкция", callback_data="get_instruction", style="primary", icon_custom_emoji_id="5992157823838984339"))
    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page_photo", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()

def get_agreement_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" Соглашение", url="https://telegra.ph/Polzovatelskoe-soglashenie-servisa-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"),
                InlineKeyboardButton(text=" Политика", url="https://telegra.ph/Politika-v-otnoshenii-obrabotki-personalnyh-dannyh-NovaAltair-11-06", style="primary", icon_custom_emoji_id="5992157823838984339"))

    return keyboard.as_markup()


def get_back_kb_photo() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page_photo", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()

def get_back_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=" Назад", callback_data="back_main_page", style="danger", icon_custom_emoji_id="5229079956545377277"))

    return keyboard.as_markup()