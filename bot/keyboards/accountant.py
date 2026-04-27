from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from services.vehicle_service import format_vehicle_number

def accountant_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бухгалтера."""
    keyboard = [
        [KeyboardButton(text="📋 Акты работ")],
        [KeyboardButton(text="🛣 Пробеги")],
        [KeyboardButton(text="ℹ️ Информация")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел"
    )

def vehicles_list_keyboard(vehicles: list, prefix: str = "acts") -> InlineKeyboardMarkup:
    """
    Клавиатура со списком машин для бухгалтера.
    prefix: 'acts' или 'mileage'
    """
    buttons = []
    for vehicle in vehicles:
        # Показываем номер машины и водителя
        label = f"🚗 {format_vehicle_number(vehicle.number)} — {vehicle.driver.full_name}"
        buttons.append([
            InlineKeyboardButton(
                text=label,
                callback_data=f"accountant_{prefix}_{vehicle.id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_to_vehicles_keyboard(prefix: str = "acts") -> InlineKeyboardMarkup:
    """Кнопка возврата к списку машин."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 К списку машин", callback_data=f"back_to_{prefix}_list")]
    ])

def act_detail_keyboard(report_id: int, prefix: str = "acts") -> InlineKeyboardMarkup:
    """Клавиатура для детального просмотра акта."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📸 Посмотреть фото", callback_data=f"view_photo_{report_id}"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад к актам", callback_data=f"back_to_vehicle_{prefix}"),
        ]
    ])