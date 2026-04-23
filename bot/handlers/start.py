from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async
from services.invite_service import process_invite_sync
from services.user_service import get_user_by_telegram_id_sync, register_driver_sync
from bot.keyboards.default import main_menu_keyboard
from bot.states.registration import RegistrationStates

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    """
    Обработчик команды /start.
    Может содержать инвайт-код: /start ABC123
    """
    telegram_id = message.from_user.id
    args = command.args

    # Используем sync_to_async для синхронных ORM-запросов
    user = await sync_to_async(get_user_by_telegram_id_sync)(telegram_id)

    if user:
        await message.answer(
            f"С возвращением, {user.full_name}!",
            reply_markup=main_menu_keyboard(user.role)
        )
        return

    if args:
        invite_code = args.strip()
        success, msg = await sync_to_async(process_invite_sync)(telegram_id, invite_code)
        await message.answer(msg)
        if success:
            user = await sync_to_async(get_user_by_telegram_id_sync)(telegram_id)
            await message.answer(
                "Главное меню:",
                reply_markup=main_menu_keyboard(user.role)
            )
        return

    # Самостоятельная регистрация водителя
    await state.set_state(RegistrationStates.waiting_for_name)
    await message.answer(
        "🚛 Добро пожаловать в систему управления автопарком!\n\n"
        "Для регистрации введите ваше ФИО (например: Иванов Иван):"
    )

@router.message(RegistrationStates.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    parts = full_name.split()
    if len(parts) < 2:
        await message.answer("Пожалуйста, введите фамилию и имя (два слова).")
        return

    first_name = parts[1]  # Имя
    last_name = parts[0]   # Фамилия

    # Создаём водителя через sync_to_async
    user = await sync_to_async(register_driver_sync)(
        message.from_user.id, first_name, last_name
    )

    await state.clear()
    await message.answer(
        f"✅ Регистрация завершена! Добро пожаловать, {user.full_name}!\n\n"
        "Теперь добавьте вашу первую машину. Отправьте госномер (например: А123ВС):",
        reply_markup=main_menu_keyboard('driver')
    )
    await state.set_state(RegistrationStates.waiting_for_vehicle_number)