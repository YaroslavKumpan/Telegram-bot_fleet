from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async

from services.user_service import get_user_by_telegram_id_sync


class RoleFilter(BaseFilter):
    def __init__(self, role: str):
        self.role = role

    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        user = await sync_to_async(get_user_by_telegram_id_sync)(obj.from_user.id)
        return user is not None and user.role == self.role