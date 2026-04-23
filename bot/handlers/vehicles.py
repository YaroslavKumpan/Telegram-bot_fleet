# bot/handlers/vehicles.py (полная переработка)
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from asgiref.sync import sync_to_async
from services.user_service import get_user_by_telegram_id_sync
from services.vehicle_service import (
    add_vehicle_for_user_sync,
    get_user_vehicles_sync,
    format_vehicle_number
)
from bot.keyboards.default import main_menu_keyboard
from bot.keyboards.vehicles import vehicles_menu_keyboard
from bot.states.registration import VehicleStates

router = Router()


@router.message(F.text == "🚗 Мои машины")
async def my_vehicles(message: Message):
    """Показывает список машин и меню управления"""
    user = await sync_to_async(get_user_by_telegram_id_sync)(message.from_user.id)
    if not user:
        await message.answer("Вы не зарегистрированы. Используйте /start")
        return

    vehicles = await sync_to_async(get_user_vehicles_sync)(message.from_user.id)

    if not vehicles:
        text = "🚗 У вас пока нет добавленных машин.\n\nНажмите «➕ Добавить машину» чтобы добавить."
    else:
        text = "🚗 Ваши машины:\n\n"
        text += "\n".join(f"• {format_vehicle_number(v.number)}" for v in vehicles)
        text += f"\n\nВсего машин: {len(vehicles)}"

    await message.answer(text, reply_markup=vehicles_menu_keyboard())


@router.message(F.text == "➕ Добавить машину")
async def add_vehicle_prompt(message: Message, state: FSMContext):
    """Запрашивает госномер для добавления"""
    await state.set_state(VehicleStates.waiting_for_vehicle_number)
    await message.answer(
        "Введите госномер автомобиля:\n\n"
        "Поддерживаемые форматы:\n"
        "• 1234 AB-7 (новый образец)\n"
        "• AB 1234-7 (новый образец)\n"
        "• А123ВС (старый образец)\n"
        "• А123ВС-7 (старый с регионом)\n\n"
        "Или нажмите «🔙 Главное меню» для отмены:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Отмена")]],
            resize_keyboard=True
        )
    )


@router.message(VehicleStates.waiting_for_vehicle_number, F.text == "🔙 Отмена")
async def cancel_add_vehicle(message: Message, state: FSMContext):
    """Отмена добавления машины"""
    await state.clear()
    await message.answer("Добавление отменено.", reply_markup=vehicles_menu_keyboard())


@router.message(VehicleStates.waiting_for_vehicle_number, F.text)
async def add_vehicle_process(message: Message, state: FSMContext):
    """Обрабатывает ввод госномера"""
    number = message.text.strip()
    telegram_id = message.from_user.id

    # Проверяем, не нажата ли случайно кнопка меню
    if number in ["🚗 Мои машины", "📸 Отправить мойку", "🧾 Отправить акт", "ℹ️ Информация"]:
        await state.clear()
        await message.answer("Добавление отменено.", reply_markup=main_menu_keyboard('driver'))
        return

    success, msg, vehicle = await sync_to_async(add_vehicle_for_user_sync)(telegram_id, number)

    if success:
        await state.clear()
        # Показываем обновлённый список машин
        vehicles = await sync_to_async(get_user_vehicles_sync)(telegram_id)
        text = f"✅ Машина {format_vehicle_number(vehicle.number)} успешно добавлена!\n\n"
        text += "🚗 Ваши машины:\n\n"
        text += "\n".join(f"• {format_vehicle_number(v.number)}" for v in vehicles)
        text += f"\n\nВсего машин: {len(vehicles)}"

        await message.answer(text, reply_markup=vehicles_menu_keyboard())
    else:
        await message.answer(
            msg + "\n\nПопробуйте ещё раз или нажмите «🔙 Отмена»:"
        )


@router.message(F.text == "🔙 Главное меню")
async def back_to_main_menu(message: Message):
    """Возврат в главное меню"""
    user = await sync_to_async(get_user_by_telegram_id_sync)(message.from_user.id)
    if not user:
        return

    await message.answer("Главное меню:", reply_markup=main_menu_keyboard(user.role))


@router.callback_query(F.data.startswith("vehicle_info_"))
async def vehicle_info(callback: CallbackQuery):
    """Показывает информацию о машине (заготовка для будущих функций)"""
    vehicle_id = int(callback.data.split("_")[-1])
    vehicles = await sync_to_async(get_user_vehicles_sync)(callback.from_user.id)
    vehicle = next((v for v in vehicles if v.id == vehicle_id), None)

    if vehicle:
        text = f"🚗 Машина: {format_vehicle_number(vehicle.number)}\n"
        text += f"📅 Добавлена: {vehicle.id} (ID в системе)\n"
        # Здесь можно добавить статистику по отчётам
        await callback.answer(f"Машина {format_vehicle_number(vehicle.number)}", show_alert=True)
    else:
        await callback.answer("Машина не найдена", show_alert=True)