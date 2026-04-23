from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apps.vehicles.models import Vehicle

def vehicle_selection_keyboard(vehicles: list[Vehicle], prefix: str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора машины из списка."""
    buttons = []
    for vehicle in vehicles:
        buttons.append([
            InlineKeyboardButton(
                text=vehicle.number,
                callback_data=f"select_vehicle_{prefix}_{vehicle.id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)