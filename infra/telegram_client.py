# infra/telegram_client.py
import requests
from django.conf import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


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
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            raise

    def send_photo_file(self, chat_id: int, photo_path: str, caption: str = '') -> dict:
        """Отправляет фото как файл."""
        url = f"{self.base_url}/sendPhoto"
        try:
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
        except FileNotFoundError:
            logger.error(f"Photo file not found: {photo_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to send photo to {chat_id}: {e}")
            raise


# Глобальный экземпляр
telegram_client = TelegramClient()