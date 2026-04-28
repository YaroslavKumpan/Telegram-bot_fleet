from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from bot.states.mileage import MileageStates
from services.mileage_service import update_mileage_sync

from bot.keyboards.default import main_menu_keyboard, vehicle_selection_keyboard
from services.user_service import get_user_by_telegram_id_sync
from services.vehicle_service import get_user_vehicles_sync, format_vehicle_number

router = Router()


@router.message(F.text == "🛣 Отправить пробег")
async def mileage_start(message: Message, state: FSMContext):
    user = await sync_to_async(get_user_by_telegram_id_sync)(message.from_user.id)
    if not user:
        return

    vehicles = await sync_to_async(get_user_vehicles_sync)(message.from_user.id)
    if not vehicles:
        await message.answer("У вас нет машин.")
        return

    if len(vehicles) == 1:
        await state.update_data(vehicle_id=vehicles[0].id)
        await state.set_state(MileageStates.waiting_for_value)
        await message.answer(
            f"🚗 {format_vehicle_number(vehicles[0].number)}\n"
            "Введите текущий пробег в километрах (только число):"
        )
    else:
        await message.answer(
            "Выберите машину:",
            reply_markup=vehicle_selection_keyboard(vehicles, "mileage")
        )


@router.callback_query(F.data.startswith("select_vehicle_mileage_"))
async def mileage_vehicle_selected(callback: CallbackQuery, state: FSMContext):
    vehicle_id = int(callback.data.split("_")[-1])
    await state.update_data(vehicle_id=vehicle_id)
    await state.set_state(MileageStates.waiting_for_value)

    vehicles = await sync_to_async(get_user_vehicles_sync)(callback.from_user.id)
    vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
    vn = format_vehicle_number(vehicle.number) if vehicle else "—"

    await callback.message.edit_text(f"🚗 {vn}\nВведите текущий пробег в км (только число):")
    await callback.answer()


@router.message(MileageStates.waiting_for_value, F.text.regexp(r'^\d+$'))
async def mileage_value_received(message: Message, state: FSMContext):
    data = await state.get_data()
    vehicle_id = data.get('vehicle_id')
    value = int(message.text.strip())

    success, msg = await sync_to_async(update_mileage_sync)(
        vehicle_id, value, message.from_user.id
    )

    await state.clear()
    await message.answer(msg, reply_markup=main_menu_keyboard('driver'))


@router.message(MileageStates.waiting_for_value)
async def mileage_invalid_value(message: Message):
    await message.answer("❌ Введите целое число (например: 125000)")