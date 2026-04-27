from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from services.vehicle_service import format_vehicle_number


def main_menu_keyboard(role: str) -> ReplyKeyboardMarkup:
    """Главное меню в зависимости от роли."""
    if role == 'driver':
        keyboard = [
            [KeyboardButton(text="📸 Отправить мойку")],
            [KeyboardButton(text="🧾 Отправить акт")],
            [KeyboardButton(text="🚗 Мои машины")],
        ]
    elif role == 'accountant':
        keyboard = [
            [KeyboardButton(text="📋 Акты работ")],
            [KeyboardButton(text="🛣 Пробеги")],
            [KeyboardButton(text="ℹ️ Информация")],
        ]
    elif role == 'director':
        keyboard = [
            [KeyboardButton(text="ℹ️ Информация")],
        ]
    else:
        keyboard = [
            [KeyboardButton(text="ℹ️ Информация")],
        ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )


def vehicles_menu_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура раздела 'Мои машины' для водителя."""
    keyboard = [
        [KeyboardButton(text="➕ Добавить машину")],
        [KeyboardButton(text="🔙 Главное меню")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )


def vehicle_selection_keyboard(vehicles: list, prefix: str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора машины (мойка/акт)."""
    buttons = []
    for vehicle in vehicles:
        buttons.append([
            InlineKeyboardButton(
                text=format_vehicle_number(vehicle.number),
                callback_data=f"select_vehicle_{prefix}_{vehicle.id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)