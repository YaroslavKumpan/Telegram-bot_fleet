import asyncio
from django.core.management.base import BaseCommand
from bot.main import main

class Command(BaseCommand):
    help = 'Запуск Telegram бота'

    def handle(self, *args, **options):
        asyncio.run(main())