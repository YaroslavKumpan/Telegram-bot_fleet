# bot/keyboards/inline.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.vehicle_service import format_vehicle_number

def vehicle_selection_keyboard(vehicles: list, prefix: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора машины.
    prefix: 'wash' или 'service'
    """
    buttons = []
    for vehicle in vehicles:
        buttons.append([
            InlineKeyboardButton(
                text=format_vehicle_number(vehicle.number),
                callback_data=f"select_vehicle_{prefix}_{vehicle.id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)