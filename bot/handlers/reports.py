# bot/handlers/reports.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from services.report_service import save_wash_report_sync, save_service_report_sync
from services.user_service import get_user_by_telegram_id_sync
from services.vehicle_service import get_user_vehicles_sync, format_vehicle_number
from bot.keyboards.default import main_menu_keyboard
from bot.keyboards.inline import vehicle_selection_keyboard
from bot.states.reports import ReportStates

router = Router()


# === Обработчики выхода из режима ожидания фото ===

@router.message(ReportStates.waiting_for_wash_photo, F.text.in_([
    "🚗 Мои машины", "🧾 Отправить акт", "ℹ️ Информация"
]))
async def cancel_wash_photo(message: Message, state: FSMContext):
    """Отмена ожидания фото мойки"""
    await state.clear()
    await message.answer("❌ Отправка отчёта о мойке отменена.",
                         reply_markup=main_menu_keyboard('driver'))


@router.message(ReportStates.waiting_for_service_photo, F.text.in_([
    "🚗 Мои машины", "📸 Отправить мойку", "ℹ️ Информация"
]))
async def cancel_service_photo(message: Message, state: FSMContext):
    """Отмена ожидания фото акта"""
    await state.clear()
    await message.answer("❌ Отправка акта отменена.",
                         reply_markup=main_menu_keyboard('driver'))


# === Обработчики для мойки ===

@router.message(F.text == "📸 Отправить мойку")
async def wash_start(message: Message, state: FSMContext):
    """Начало процесса отправки мойки"""
    user = await sync_to_async(get_user_by_telegram_id_sync)(message.from_user.id)
    if not user:
        await message.answer("Вы не зарегистрированы. Используйте /start")
        return

    vehicles = await sync_to_async(get_user_vehicles_sync)(message.from_user.id)

    if not vehicles:
        await message.answer(
            "У вас нет привязанных машин. "
            "Добавьте машину в разделе «🚗 Мои машины»."
        )
        return

    if len(vehicles) == 1:
        await state.update_data(vehicle_id=vehicles[0].id)
        await state.set_state(ReportStates.waiting_for_wash_photo)
        await message.answer(
            f"🚗 Машина: {format_vehicle_number(vehicles[0].number)}\n\n"
            "📸 Отправьте фото мойки\n"
            "(или нажмите другую кнопку меню для отмены):"
        )
    else:
        await message.answer(
            "Выберите машину для отчёта о мойке:",
            reply_markup=vehicle_selection_keyboard(vehicles, "wash")
        )


@router.callback_query(F.data.startswith("select_vehicle_wash_"))
async def wash_vehicle_selected(callback: CallbackQuery, state: FSMContext):
    """Выбор машины для мойки через inline-клавиатуру"""
    vehicle_id = int(callback.data.split("_")[-1])

    await state.update_data(vehicle_id=vehicle_id)
    await state.set_state(ReportStates.waiting_for_wash_photo)

    vehicles = await sync_to_async(get_user_vehicles_sync)(callback.from_user.id)
    vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
    vehicle_number = format_vehicle_number(vehicle.number) if vehicle else "Неизвестно"

    await callback.message.edit_text(
        f"🚗 Машина: {vehicle_number}\n\n"
        "📸 Отправьте фото мойки\n"
        "(или нажмите другую кнопку меню для отмены):"
    )
    await callback.answer()


@router.message(ReportStates.waiting_for_wash_photo, F.photo)
async def wash_photo_received(message: Message, state: FSMContext):
    """Получение и сохранение фото мойки"""
    data = await state.get_data()
    vehicle_id = data.get('vehicle_id')

    if not vehicle_id:
        await message.answer("❌ Ошибка: не выбрана машина. Начните заново.")
        await state.clear()
        return

    photo_file_id = message.photo[-1].file_id

    processing_msg = await message.answer("⏳ Сохраняю отчёт...")

    success, msg, report = await sync_to_async(save_wash_report_sync)(vehicle_id, photo_file_id)

    await processing_msg.delete()
    await message.answer(msg, reply_markup=main_menu_keyboard('driver'))
    await state.clear()


# === Обработчики для актов ===

@router.message(F.text == "🧾 Отправить акт")
async def service_start(message: Message, state: FSMContext):
    """Начало процесса отправки акта"""
    user = await sync_to_async(get_user_by_telegram_id_sync)(message.from_user.id)
    if not user:
        await message.answer("Вы не зарегистрированы. Используйте /start")
        return

    vehicles = await sync_to_async(get_user_vehicles_sync)(message.from_user.id)

    if not vehicles:
        await message.answer(
            "У вас нет привязанных машин. "
            "Добавьте машину в разделе «🚗 Мои машины»."
        )
        return

    if len(vehicles) == 1:
        await state.update_data(vehicle_id=vehicles[0].id)
        await state.set_state(ReportStates.waiting_for_service_photo)
        await message.answer(
            f"🚗 Машина: {format_vehicle_number(vehicles[0].number)}\n\n"
            "🧾 Отправьте фото акта\n"
            "(или нажмите другую кнопку меню для отмены):"
        )
    else:
        await message.answer(
            "Выберите машину для акта:",
            reply_markup=vehicle_selection_keyboard(vehicles, "service")
        )


@router.callback_query(F.data.startswith("select_vehicle_service_"))
async def service_vehicle_selected(callback: CallbackQuery, state: FSMContext):
    """Выбор машины для акта через inline-клавиатуру"""
    vehicle_id = int(callback.data.split("_")[-1])

    await state.update_data(vehicle_id=vehicle_id)
    await state.set_state(ReportStates.waiting_for_service_photo)

    vehicles = await sync_to_async(get_user_vehicles_sync)(callback.from_user.id)
    vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
    vehicle_number = format_vehicle_number(vehicle.number) if vehicle else "Неизвестно"

    await callback.message.edit_text(
        f"🚗 Машина: {vehicle_number}\n\n"
        "🧾 Отправьте фото акта\n"
        "(или нажмите другую кнопку меню для отмены):"
    )
    await callback.answer()


@router.message(ReportStates.waiting_for_service_photo, F.photo)
async def service_photo_received(message: Message, state: FSMContext):
    """Получение и сохранение фото акта"""
    data = await state.get_data()
    vehicle_id = data.get('vehicle_id')

    if not vehicle_id:
        await message.answer("❌ Ошибка: не выбрана машина. Начните заново.")
        await state.clear()
        return

    photo_file_id = message.photo[-1].file_id

    processing_msg = await message.answer("⏳ Сохраняю акт...")

    success, msg, report = await sync_to_async(save_service_report_sync)(vehicle_id, photo_file_id)

    await processing_msg.delete()
    await message.answer(msg, reply_markup=main_menu_keyboard('driver'))
    await state.clear()