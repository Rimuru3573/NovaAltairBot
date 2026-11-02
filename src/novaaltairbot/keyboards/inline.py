from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from novaaltairbot.api.schemas import UserOut

def main_keybord(user: UserOut):
    keyboard = InlineKeyboardBuilder()

    if user.is_new == True:
        keyboard.row(InlineKeyboardButton(text="Пробная подписка", callback_data="get_free_sub", style="success", icon_custom_emoji_id="5429388216094444138"))
    else:
        keyboard.row(InlineKeyboardButton(text="Основная подписка", callback_data="get_my_subs", style="primary", icon_custom_emoji_id="5429388216094444138"))
    keyboard.row(InlineKeyboardButton(text="Приобрести подписку", callback_data="get_sub", style="primary", icon_custom_emoji_id="5224428833381302949"))
    keyboard.row(InlineKeyboardButton(text="Инструкция", callback_data="get_instruction", style="primary", icon_custom_emoji_id="5438151723199792420"),
                 InlineKeyboardButton(text="Пригласить друга", callback_data="new_friend_page", style="primary", icon_custom_emoji_id="6019363826024061450"),
                 InlineKeyboardButton(text="Новости", url="https://t.me/мой_канал", style="primary", icon_custom_emoji_id="5877597667231534929"))
    keyboard.row(InlineKeyboardButton(text="Личный кабинет", callback_data="get_profile", style="primary", icon_custom_emoji_id="5879770735999717115"),
                 InlineKeyboardButton(text="Поддержка", url="https://t.me/zxcurs4d", style="primary", icon_custom_emoji_id="5884510167986343350"))

    return keyboard.as_markup()