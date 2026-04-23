from aiogram import Router, F
from aiogram.types import Message
from services.user_service import get_user_by_telegram_id
from bot.keyboards.inline import vehicle_selection_keyboard
from apps.vehicles.models import Vehicle

router = Router()

@router.message(F.text == "📸 Отправить мойку")
async def send_wash_start(message: Message):
    user = get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Вы не зарегистрированы.")
        return

    vehicles = list(user.vehicles.all())
    if not vehicles:
        await message.answer(
            "У вас нет привязанных машин. "
            "Добавьте машину через кнопку «🚗 Мои машины»."
        )
        return

    if len(vehicles) == 1:
        # Если одна машина — сразу запрашиваем фото
        from bot.states.reports import ReportStates
        from aiogram.fsm.context import FSMContext

        # Сохраним vehicle_id в состоянии
        # Но для начала просто попросим фото
        await message.answer(
            f"Выбрана машина {vehicles[0].number}. Отправьте фото мойки:"
        )
        # TODO: перейти в состояние waiting_for_wash_photo и сохранить vehicle_id
    else:
        # Несколько машин — показываем клавиатуру выбора
        await message.answer(
            "Выберите машину:",
            reply_markup=vehicle_selection_keyboard(vehicles, "wash")
        )

@router.message(F.text == "🧾 Отправить акт")
async def send_service_start(message: Message):
    user = get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Вы не зарегистрированы.")
        return

    vehicles = list(user.vehicles.all())
    if not vehicles:
        await message.answer("У вас нет привязанных машин.")
        return

    if len(vehicles) == 1:
        await message.answer(
            f"Выбрана машина {vehicles[0].number}. Отправьте фото акта:"
        )
        # TODO: FSM
    else:
        await message.answer(
            "Выберите машину:",
            reply_markup=vehicle_selection_keyboard(vehicles, "service")
        )

@router.message(F.text == "🚗 Мои машины")
async def my_vehicles(message: Message):
    user = get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Вы не зарегистрированы.")
        return

    vehicles = user.vehicles.all()
    if not vehicles:
        await message.answer(
            "У вас пока нет машин.\n"
            "Отправьте госномер для добавления (например: А123ВС):"
        )
        # TODO: FSM для добавления машины
    else:
        text = "Ваши машины:\n" + "\n".join(f"- {v.number}" for v in vehicles)
        text += "\n\nЧтобы добавить новую, отправьте госномер."
        await message.answer(text)
        # TODO: FSM для добавления

@router.message(F.text == "ℹ️ Информация")
async def info(message: Message):
    user = get_user_by_telegram_id(message.from_user.id)
    if not user:
        return

    if user.role == 'accountant':
        await message.answer(
            "Вы подключены как бухгалтер.\n"
            "Вам будут приходить уведомления о новых актах выполненных работ."
        )
    elif user.role == 'director':
        await message.answer(
            "Вы подключены как директор.\n"
            "Вам доступна административная панель для управления системой.\n"
            "Также вы будете получать уведомления о нарушениях графика мойки."
        )