LEXICON = {
    "start_msg": "<b>Главное меню</b>\n<i>NovaAltairVpn</i> - главное простота.",
    "plug": "Упс, эта функция еще не добавлена, но совсем скоро реализуется!",
    "first_msg": (
        '<tg-emoji emoji-id="5936017305585586269">🪪</tg-emoji> Логин: <code>{username}</code>\n'
        '<tg-emoji emoji-id="5936017305585586269">🪪</tg-emoji> Пароль: <code>{password}</code>\n'
        '<tg-emoji emoji-id="5274099962655816924">❗</tg-emoji> <b>ВНИМАНИЕ:</b> обязательно сохраните или перешлите это сообщение в избранное, пароль выдается один раз. <b>МЫ ЕГО НЕ ХРАНИМ</b><tg-emoji emoji-id="5274099962655816924">❗</tg-emoji>\n\n'
        'Продолжая пользоваться ботом вы соглашаетесь с Политикой конфиденциальности и Пользовательским соглашением.'
    ),
    "rate": '<tg-emoji emoji-id="5260730055880876557">🔗</tg-emoji> <b>Выберите тариф</b>',
    "get_connect": (
        '<tg-emoji emoji-id="5260730055880876557">🔗</tg-emoji> <b>Добавить подключение</b>\n'
        '<tg-emoji emoji-id="5357069174512303778">✅</tg-emoji> Выберите приложение — подписка добавится сама\n'
        '<tg-emoji emoji-id="5992157823838984339">📖</tg-emoji> Нет ни одного? Начните с <a href="https://play.google.com/store/apps/details?id=com.happproxy"><b>Happ</b></a>'
    ),
    "instruction":(
        '<tg-emoji emoji-id="5992157823838984339">📖</tg-emoji> <b>Как подключиться</b>\n\n'
        '1. Установите приложение Happ для вашей системы.\n'
        '2. Нажмите кнопку подключения — ссылка добавится сама, или скопируйте и вставьте вручную в свое приложение.\n'
        '3. Выберите страну и включите тумблер.'
    ),
    "referral_page": (
        '<tg-emoji emoji-id="5453965363286925977">🤝</tg-emoji> <b>Реферальная система</b>\n\n'
        '<tg-emoji emoji-id="5258513401784573443">👥</tg-emoji> Приглашено: <b>{referrals}</b>\n'
        '<tg-emoji emoji-id="5807499888245612254">💳</tg-emoji> Доступно <b>{days}</b>\n\n'
        'Приглашайте друзей и получайте бесплатное продление на {referrals_day} дней к подписке за каждого приглашенного, нажавшего start\n\n'
        '<tg-emoji emoji-id="5260730055880876557">🔗</tg-emoji> <b>Ваша ссылка</b>\n<code>{link}</code>'
    ),
    "referral_kb": 'Попробуй AltairVpn и помоги другу получить бонусы!',
    "referral_0": 'Вы пока никого не пригласили!',
    "devices": (
        '<tg-emoji emoji-id="5258508428212445001">🎮</tg-emoji> <b>Ваши устройства</b>\n'
        '<tg-emoji emoji-id="5357069174512303778">✅</tg-emoji> Занято мест: {hwid} из {limit_hwid}\n\n'
        'Чтобы удалить устройства нажмите <b>перевыпуск</b>. Осторожно, это удалит все подключенные устройствам и заменит нынешнюю ссылку на новую.'
        ),
}


def get_sub(username: str, expiry_time: str, sub: str, hwid: int, limit_hwid: int) -> str:
    text = '<tg-emoji emoji-id="5260730055880876557">🔗</tg-emoji> <b>Основной ключ</b>\n\n'
    text += f'<tg-emoji emoji-id="5260730055880876557">🔗</tg-emoji> Ваш username: <code>{username}</code>\n'
    text += f'<tg-emoji emoji-id="5778605968208170641">🗓️</tg-emoji> Активна до <b>{expiry_time}</b>\n'
    text += f'<tg-emoji emoji-id="5258508428212445001">🎮</tg-emoji> Устройств {hwid} из {limit_hwid}\n\n'
    text += 'Скопируйте ключ ниже или нажмите «Подключиться» — ссылка подставится сама\n'
    text += f'<code>{sub}</code>'

    return text


def get_profile(name: str, username: str, referrals: str, payment_id: str | None = None, expiry_time: str | None = None) -> str:
    text = '<tg-emoji emoji-id="5936017305585586269">🪪</tg-emoji> <b>Личный кабинет</b>\n\n'
    if name:
        text += f'<tg-emoji emoji-id="5936017305585586269">🪪</tg-emoji> @{name}\n'

    text += f'<tg-emoji emoji-id="5936017305585586269">🪪</tg-emoji> Username: <code>{username}</code>\n'
    if expiry_time:
        text += f'<tg-emoji emoji-id="5778605968208170641">🗓️</tg-emoji> Активна до <b>{expiry_time}</b>\n'
    else: 
        text += '<tg-emoji emoji-id="5778605968208170641">🗓️</tg-emoji> Подписка <b>неактивна</b>\n\n'
    text += f'<tg-emoji emoji-id="5258513401784573443">👥</tg-emoji> Приглашено: <b>{referrals}</b>\n'
    if payment_id:
        text += f'<tg-emoji emoji-id="5283232570660634549">👛</tg-emoji> Payment id: <code>{payment_id}</code>'

    return text
