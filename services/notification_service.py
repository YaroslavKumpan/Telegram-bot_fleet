# services/notification_service.py
from apps.users.models import User
from apps.reports.models import ServiceReport
from services.vehicle_service import format_vehicle_number
from infra.telegram_client import telegram_client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def notify_accountants_about_report(report_id: int):
    """
    Отправляет уведомление всем бухгалтерам о новом акте.
    Эта функция вызывается в Celery задаче.
    """
    try:
        report = ServiceReport.objects.select_related(
            'vehicle', 'vehicle__driver'
        ).get(id=report_id)
    except ServiceReport.DoesNotExist:
        logger.error(f"ServiceReport with id={report_id} not found")
        return

    accountants = User.objects.filter(
        role=User.Role.ACCOUNTANT,
        telegram_id__isnull=False
    )

    if not accountants.exists():
        logger.info("No accountants to notify")
        return

    # Формируем текст уведомления
    driver_name = report.vehicle.driver.full_name
    vehicle_number = format_vehicle_number(report.vehicle.number)
    date_str = report.created_at.strftime('%d.%m.%Y в %H:%M')

    caption = (
        f"🧾 <b>Новый акт выполненных работ</b>\n\n"
        f"👤 Водитель: {driver_name}\n"
        f"🚗 Машина: {vehicle_number}\n"
        f"📅 Дата: {date_str}"
    )

    # Получаем URL фото
    if report.photo:
        photo_url = f"https://parkauto.ru{report.photo.url}"
    else:
        photo_url = None

    # Отправляем уведомления
    for accountant in accountants:
        try:
            if photo_url:
                telegram_client.send_photo(
                    chat_id=accountant.telegram_id,
                    photo_url=photo_url,
                    caption=caption
                )
            else:
                telegram_client.send_message(
                    chat_id=accountant.telegram_id,
                    text=caption + "\n\n⚠️ Фото недоступно"
                )
            logger.info(f"Notification sent to accountant {accountant.telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send notification to {accountant.telegram_id}: {e}")


def notify_directors_about_violations(violations: list):
    """
    Отправляет уведомление директорам о нарушениях графика мойки.
    violations — список кортежей (vehicle, days_since_wash)
    """
    directors = User.objects.filter(
        role=User.Role.DIRECTOR,
        telegram_id__isnull=False
    )

    if not directors.exists() or not violations:
        return

    # Группируем нарушения по водителям
    from collections import defaultdict
    by_driver = defaultdict(list)

    for vehicle, days in violations:
        by_driver[vehicle.driver].append((vehicle, days))

    # Формируем текст
    text = "⚠️ <b>Нарушения графика мойки</b>\n\n"
    text += f"📅 Проверка от {__import__('django').utils.timezone.now().strftime('%d.%m.%Y')}\n\n"

    for driver, vehicle_list in by_driver.items():
        text += f"👤 <b>{driver.full_name}</b>:\n"
        for vehicle, days in vehicle_list:
            text += f"  • {format_vehicle_number(vehicle.number)} — {days} дн. без мойки\n"
        text += "\n"

    for director in directors:
        try:
            telegram_client.send_message(
                chat_id=director.telegram_id,
                text=text
            )
        except Exception as e:
            logger.error(f"Failed to send violation to director {director.telegram_id}: {e}")