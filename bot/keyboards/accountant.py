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

def vehicles_list_keyboard(vehicles: list, prefix: str = "acts", use_accountant_prefix: bool = True) -> InlineKeyboardMarkup:
    """
    prefix: например "director_wash", "director_acts", "acts"
    use_accountant_prefix: если True, добавляет "accountant_" (для бухгалтера).
    """
    buttons = []
    for vehicle in vehicles:
        cb_prefix = "accountant_" if use_accountant_prefix else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"🚗 {format_vehicle_number(vehicle.number)} — {vehicle.driver.full_name}",
                callback_data=f"{cb_prefix}{prefix}_{vehicle.id}"
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