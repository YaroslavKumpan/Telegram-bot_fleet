# bot/handlers/menu.py
from aiogram import Router, F
from aiogram.types import Message
from asgiref.sync import sync_to_async
from services.user_service import get_user_by_telegram_id_sync

router = Router()

@router.message(F.text == "ℹ️ Информация")
async def info(message: Message):
    user = await sync_to_async(get_user_by_telegram_id_sync)(message.from_user.id)
    if not user:
        return

    if user.role == 'accountant':
        await message.answer(
            "ℹ️ Вы подключены как бухгалтер.\n\n"
            "📋 Вам будут автоматически приходить уведомления о новых актах "
            "выполненных работ с фото и данными водителя."
        )
    elif user.role == 'director':
        await message.answer(
            "ℹ️ Вы подключены как директор.\n\n"
            "📊 Вам доступна административная панель для управления системой.\n"
            "⚠️ Вы будете получать уведомления о нарушениях графика мойки."
        )
    elif user.role == 'driver':
        await message.answer(
            "ℹ️ Вы подключены как водитель.\n\n"
            "📸 Используйте кнопки меню для отправки фотоотчётов.\n"
            "🚗 В разделе «Мои машины» вы можете добавить автомобили."
        )