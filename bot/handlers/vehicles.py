from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from asgiref.sync import sync_to_async

from bot.keyboards.default import main_menu_keyboard, vehicles_menu_keyboard
from bot.states.registration import VehicleStates, RegistrationStates
from services.user_service import get_user_by_telegram_id_sync
from services.vehicle_service import (
    add_vehicle_for_user_sync,
    get_user_vehicles_sync,
    format_vehicle_number
)

router = Router()


@router.message(F.text == "🚗 Мои машины")
async def my_vehicles(message: Message):
    """Показывает список машин и меню управления."""
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
    """Запрашивает госномер для добавления."""
    await state.set_state(VehicleStates.waiting_for_vehicle_number)

    cancel_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Отмена")]],
        resize_keyboard=True,
        input_field_placeholder="Введите госномер"
    )

    await message.answer(
        "Введите госномер автомобиля:\n\n"
        "Поддерживаемые форматы:\n"
        "• 1234 AB-7 (новый образец)\n"
        "• AB 1234-7 (новый образец)\n"
        "• А123ВС (старый образец)\n"
        "• А123ВС-7 (старый с регионом)\n\n"
        "Или нажмите «🔙 Отмена» для отмены:",
        reply_markup=cancel_keyboard
    )


@router.message(VehicleStates.waiting_for_vehicle_number, F.text == "🔙 Отмена")
async def cancel_add_vehicle(message: Message, state: FSMContext):
    """Отмена добавления машины."""
    await state.clear()
    await message.answer("Добавление отменено.", reply_markup=vehicles_menu_keyboard())


@router.message(VehicleStates.waiting_for_vehicle_number, F.text.in_([
    "🚗 Мои машины", "📸 Отправить мойку", "🧾 Отправить акт", "ℹ️ Информация"
]))
async def cancel_add_on_menu(message: Message, state: FSMContext):
    """Отмена добавления при нажатии кнопки меню."""
    await state.clear()
    user = await sync_to_async(get_user_by_telegram_id_sync)(message.from_user.id)
    await message.answer("Добавление отменено.", reply_markup=main_menu_keyboard(user.role if user else 'driver'))


@router.message(VehicleStates.waiting_for_vehicle_number, F.text)
async def add_vehicle_process(message: Message, state: FSMContext):
    """Обрабатывает ввод госномера."""
    number = message.text.strip()
    telegram_id = message.from_user.id

    success, msg, vehicle = await sync_to_async(add_vehicle_for_user_sync)(telegram_id, number)

    if success:
        await state.clear()
        vehicles = await sync_to_async(get_user_vehicles_sync)(telegram_id)
        text = f"✅ Машина {format_vehicle_number(vehicle.number)} успешно добавлена!\n\n"
        text += "🚗 Ваши машины:\n\n"
        text += "\n".join(f"• {format_vehicle_number(v.number)}" for v in vehicles)
        text += f"\n\nВсего машин: {len(vehicles)}"

        await message.answer(text, reply_markup=vehicles_menu_keyboard())
    else:
        await message.answer(msg + "\n\nПопробуйте ещё раз или нажмите «🔙 Отмена»:")


@router.message(F.text == "🔙 Главное меню")
async def back_to_main_menu(message: Message):
    """Возврат в главное меню."""
    user = await sync_to_async(get_user_by_telegram_id_sync)(message.from_user.id)
    if not user:
        return

    await message.answer("Главное меню:", reply_markup=main_menu_keyboard(user.role))


@router.message(RegistrationStates.waiting_for_vehicle_number, F.text)
async def add_first_vehicle(message: Message, state: FSMContext):
    """Добавление первой машины после регистрации."""
    number = message.text.strip()
    telegram_id = message.from_user.id

    # Проверка, что не нажата какая-то кнопка
    if number in ["🚗 Мои машины", "📸 Отправить мойку", "🧾 Отправить акт", "ℹ️ Информация"]:
        await state.clear()
        await message.answer("Добавление отменено.", reply_markup=main_menu_keyboard('driver'))
        return

    try:
        success, msg, vehicle = await sync_to_async(add_vehicle_for_user_sync)(telegram_id, number)
        if success:
            await state.clear()
            await message.answer(
                f"{msg}\n\nТеперь вы можете отправить фото мойки или акта.",
                reply_markup=main_menu_keyboard('driver')
            )
        else:
            await message.answer(msg + "\n\nПопробуйте ещё раз:")
    except Exception as e:
        # Логируем ошибку и сообщаем пользователю
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при добавлении первой машины: {e}")
        await message.answer("❌ Произошла внутренняя ошибка. Попробуйте позже или обратитесь к администратору.")
