# bot/main.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config.settings import BOT_TOKEN
from bot.handlers.start import router as start_router
from bot.handlers.vehicles import router as vehicles_router
from bot.handlers.reports import router as reports_router
from bot.handlers.menu import router as menu_router

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не указан в настройках!")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(vehicles_router)
dp.include_router(reports_router)
dp.include_router(menu_router)

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)