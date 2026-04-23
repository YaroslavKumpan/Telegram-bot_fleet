# bot/keyboards/vehicles.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from services.vehicle_service import format_vehicle_number

def vehicles_menu_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура раздела 'Мои машины'"""
    keyboard = [
        [KeyboardButton(text="➕ Добавить машину")],
        [KeyboardButton(text="🔙 Главное меню")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

def vehicle_list_keyboard(vehicles: list) -> InlineKeyboardMarkup:
    """
    Inline-клавиатура со списком машин.
    Позволяет удалить машину (опционально).
    """
    buttons = []
    for vehicle in vehicles:
        buttons.append([
            InlineKeyboardButton(
                text=f"🚗 {format_vehicle_number(vehicle.number)}",
                callback_data=f"vehicle_info_{vehicle.id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def main_menu_keyboard(role: str) -> ReplyKeyboardMarkup:
    """Главное меню в зависимости от роли."""
    if role == 'driver':
        keyboard = [
            [KeyboardButton(text="📸 Отправить мойку")],
            [KeyboardButton(text="🧾 Отправить акт")],
            [KeyboardButton(text="🚗 Мои машины")],
        ]
    else:
        keyboard = [
            [KeyboardButton(text="ℹ️ Информация")]
        ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )