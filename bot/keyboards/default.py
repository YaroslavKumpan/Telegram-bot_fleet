from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard(role: str) -> ReplyKeyboardMarkup:
    """Главное меню в зависимости от роли."""
    if role == 'driver':
        keyboard = [
            [KeyboardButton(text="📸 Отправить мойку")],
            [KeyboardButton(text="🧾 Отправить акт")],
            [KeyboardButton(text="🚗 Мои машины")],
        ]
    else:
        # Бухгалтер и директор видят только информационное сообщение
        keyboard = [
            [KeyboardButton(text="ℹ️ Информация")]
        ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )