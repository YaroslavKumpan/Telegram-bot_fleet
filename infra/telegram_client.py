# infra/telegram_client.py
import requests
from django.conf import settings
from typing import Optional


class TelegramClient:
    """Синхронный клиент для отправки сообщений через Telegram API."""

    def __init__(self):
        self.token = settings.BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id: int, text: str) -> dict:
        """Отправляет текстовое сообщение."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    def send_photo(self, chat_id: int, photo_url: str, caption: str = '') -> dict:
        """Отправляет фото по URL."""
        url = f"{self.base_url}/sendPhoto"
        payload = {
            'chat_id': chat_id,
            'photo': photo_url,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()

    def send_photo_file(self, chat_id: int, photo_path: str, caption: str = '') -> dict:
        """Отправляет фото как файл."""
        url = f"{self.base_url}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, files=files, timeout=15)
            response.raise_for_status()
        return response.json()


# Глобальный экземпляр для использования в задачах
telegram_client = TelegramClient()