# services/report_service.py
from apps.reports.models import WashReport, ServiceReport
from apps.vehicles.models import Vehicle
import requests
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone


def download_telegram_photo(file_id: str) -> bytes:
    """
    Скачивает фото с серверов Telegram по file_id.
    Возвращает байты фото.
    """
    try:
        # Получаем file_path через Telegram Bot API
        url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getFile"
        response = requests.get(url, params={"file_id": file_id}, timeout=15)
        response.raise_for_status()

        file_path = response.json()["result"]["file_path"]

        # Скачиваем сам файл
        download_url = f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_path}"
        photo_response = requests.get(download_url, timeout=30)
        photo_response.raise_for_status()

        return photo_response.content
    except Exception as e:
        raise Exception(f"Ошибка скачивания фото: {str(e)}")


def save_wash_report_sync(vehicle_id: int, photo_file_id: str) -> tuple:
    """
    Сохраняет отчёт о мойке.
    Возвращает (успех, сообщение, report/None).
    """
    try:
        vehicle = Vehicle.objects.select_related('driver').get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return False, "❌ Машина не найдена.", None

    try:
        # Скачиваем фото
        photo_bytes = download_telegram_photo(photo_file_id)

        # Создаём отчёт
        report = WashReport(vehicle=vehicle)

        # Формируем имя файла (используем текущее время, а не report.created_at)
        now = timezone.now()
        file_name = f"wash_{vehicle.number}_{now:%Y%m%d_%H%M%S}.jpg"

        # Сохраняем фото
        report.photo.save(file_name, ContentFile(photo_bytes), save=False)
        report.save()

        return True, "✅ Отчёт о мойке успешно отправлен!", report

    except Exception as e:
        return False, f"❌ Ошибка при сохранении: {str(e)}", None


def save_service_report_sync(vehicle_id: int, photo_file_id: str) -> tuple:
    """
    Сохраняет акт выполненных работ.
    Возвращает (успех, сообщение, report/None).
    """
    try:
        vehicle = Vehicle.objects.select_related('driver').get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return False, "❌ Машина не найдена.", None

    try:
        # Скачиваем фото
        photo_bytes = download_telegram_photo(photo_file_id)

        # Создаём отчёт
        report = ServiceReport(vehicle=vehicle)

        # Формируем имя файла (используем текущее время)
        now = timezone.now()
        file_name = f"service_{vehicle.number}_{now:%Y%m%d_%H%M%S}.jpg"

        # Сохраняем фото
        report.photo.save(file_name, ContentFile(photo_bytes), save=False)
        report.save()

        return True, "✅ Акт выполненных работ успешно отправлен!", report

    except Exception as e:
        return False, f"❌ Ошибка при сохранении: {str(e)}", None