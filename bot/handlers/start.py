from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from services.invite_service import process_invite
from services.user_service import get_user_by_telegram_id
from bot.keyboards.default import main_menu_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, command: CommandObject):
    """
    Обработчик команды /start.
    Может содержать инвайт-код: /start ABC123
    """
    telegram_id = message.from_user.id
    args = command.args  # строка после /start

    # Проверяем, есть ли уже такой пользователь
    user = get_user_by_telegram_id(telegram_id)

    if user:
        # Пользователь уже привязан — просто показываем меню
        await message.answer(
            f"С возвращением, {user.full_name}!",
            reply_markup=main_menu_keyboard(user.role)
        )
        return

    # Если пользователь новый и есть аргумент — обрабатываем инвайт
    if args:
        invite_code = args.strip()
        success, msg = process_invite(telegram_id, invite_code)
        await message.answer(msg)
        if success:
            user = get_user_by_telegram_id(telegram_id)
            await message.answer(
                "Главное меню:",
                reply_markup=main_menu_keyboard(user.role)
            )
        return

    # Если нет инвайта и пользователь не найден — возможно, самовольная регистрация водителя
    # По заданию водитель может регистрироваться сам. Реализуем это:
    await message.answer(
        "Добро пожаловать! Похоже, вы новый водитель.\n"
        "Введите вашу фамилию и имя (например: Иванов Иван):"
    )
    # Здесь нужно будет состояние FSM для регистрации — добавим позже