import logging
import os
from collections import defaultdict

from django.utils import timezone

from apps.reports.models import ServiceReport
from apps.users.models import User
from infra.telegram_client import telegram_client
from services.vehicle_service import format_vehicle_number

logger = logging.getLogger(__name__)


def notify_accountants_about_report(report_id: int):
    """
    Отправляет уведомление всем бухгалтерам о новом акте.
    Вызывается в Celery задаче сразу после создания акта.
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

    driver_name = report.vehicle.driver.full_name
    vehicle_number = format_vehicle_number(report.vehicle.number)
    date_str = report.created_at.strftime('%d.%m.%Y в %H:%M')

    caption = (
        f"🧾 <b>Новый акт выполненных работ</b>\n\n"
        f"👤 Водитель: {driver_name}\n"
        f"🚗 Машина: {vehicle_number}\n"
        f"📅 Дата: {date_str}"
    )

    for accountant in accountants:
        try:
            if report.photo and os.path.exists(report.photo.path):
                telegram_client.send_photo_file(
                    chat_id=accountant.telegram_id,
                    photo_path=report.photo.path,
                    caption=caption
                )
                logger.info(f"Notification with photo sent to {accountant.telegram_id}")
            else:
                telegram_client.send_message(
                    chat_id=accountant.telegram_id,
                    text=caption + "\n\n⚠️ Фото недоступно"
                )
                logger.info(f"Text notification sent to {accountant.telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send notification to {accountant.telegram_id}: {e}")


def notify_accountants_daily_report(reports_by_driver: dict, date):
    """
    Отправляет бухгалтерам сводку актов за день, сгруппированную по водителям.

    Args:
        reports_by_driver: словарь {driver: [reports]}
        date: дата, за которую формируется сводка
    """
    # Использует: User (из apps.users.models) — импортирован вверху
    accountants = User.objects.filter(
        role=User.Role.ACCOUNTANT,
        telegram_id__isnull=False
    )

    if not accountants.exists():
        logger.info("No accountants to notify")
        return

    # Использует: format_vehicle_number (из services.vehicle_service) — импортирован вверху
    date_str = date.strftime('%d.%m.%Y')
    text = f"📋 <b>Сводка актов за {date_str}</b>\n\n"

    total_acts = 0
    for driver, reports in reports_by_driver.items():
        text += f"👤 <b>{driver.full_name}</b> ({len(reports)} акт.):\n"
        for report in reports:
            vehicle_number = format_vehicle_number(report.vehicle.number)
            time_str = report.created_at.strftime('%H:%M')
            text += f"  • {vehicle_number} — {time_str}\n"
        text += "\n"
        total_acts += len(reports)

    text += f"📊 <b>Всего актов за день: {total_acts}</b>"

    # Использует: telegram_client (из infra.telegram_client) — импортирован вверху
    for accountant in accountants:
        try:
            telegram_client.send_message(
                chat_id=accountant.telegram_id,
                text=text
            )
            logger.info(f"Daily report sent to accountant {accountant.telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send daily report to {accountant.telegram_id}: {e}")


def notify_directors_about_violations(violations: list):
    """
    Отправляет уведомление директорам о нарушениях графика мойки.

    Args:
        violations: список кортежей (vehicle, days_since_wash)
    """
    # Использует: User (из apps.users.models) — импортирован вверху
    directors = User.objects.filter(
        role=User.Role.DIRECTOR,
        telegram_id__isnull=False
    )

    if not directors.exists() or not violations:
        return

    # Использует: defaultdict (из collections) — импортирован вверху
    by_driver = defaultdict(list)

    for vehicle, days in violations:
        by_driver[vehicle.driver].append((vehicle, days))

    # Использует: timezone (из django.utils) — импортирован вверху
    text = "⚠️ <b>Нарушения графика мойки</b>\n\n"
    text += f"📅 Проверка от {timezone.now().strftime('%d.%m.%Y')}\n\n"

    for driver, vehicle_list in by_driver.items():
        text += f"👤 <b>{driver.full_name}</b>:\n"
        for vehicle, days in vehicle_list:
            # Использует: format_vehicle_number (из services.vehicle_service) — импортирован вверху
            text += f"  • {format_vehicle_number(vehicle.number)} — {days} дн. без мойки\n"
        text += "\n"

    # Использует: telegram_client (из infra.telegram_client) — импортирован вверху
    for director in directors:
        try:
            telegram_client.send_message(
                chat_id=director.telegram_id,
                text=text
            )
        except Exception as e:
            logger.error(f"Failed to send violation to director {director.telegram_id}: {e}")