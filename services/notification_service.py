import logging
import os
from datetime import date, timedelta
from django.db.models import Max
from django.utils import timezone
from apps.reports.models import ServiceReport, WashReport
from apps.users.models import User
from apps.vehicles.models import Vehicle
from infra.telegram_client import telegram_client
from services.vehicle_service import format_vehicle_number

logger = logging.getLogger(__name__)


def notify_accountants_about_report(report_id: int):
    """
    Отправляет уведомление всем бухгалтерам о новом акте.
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

    # Отправляем уведомления
    for accountant in accountants:
        try:
            if report.photo and os.path.exists(report.photo.path):
                # Отправляем фото как файл
                telegram_client.send_photo_file(
                    chat_id=accountant.telegram_id,
                    photo_path=report.photo.path,
                    caption=caption
                )
                logger.info(f"Notification with photo sent to {accountant.telegram_id}")
            else:
                # Если фото нет — отправляем только текст
                telegram_client.send_message(
                    chat_id=accountant.telegram_id,
                    text=caption + "\n\n⚠️ Фото недоступно"
                )
                logger.info(f"Text notification sent to {accountant.telegram_id}")

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
    from django.utils import timezone
    text = "⚠️ <b>Нарушения графика мойки</b>\n\n"
    text += f"📅 Проверка от {timezone.now().strftime('%d.%m.%Y')}\n\n"

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

def notify_accountants_daily_report(reports_by_driver: dict, date):
    """Ежедневная сводка актов, сгруппированная по водителям."""
    accountants = User.objects.filter(
        role=User.Role.ACCOUNTANT,
        telegram_id__isnull=False
    )
    if not accountants.exists():
        logger.info("No accountants to notify")
        return

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

    for accountant in accountants:
        try:
            telegram_client.send_message(
                chat_id=accountant.telegram_id,
                text=text
            )
        except Exception as e:
            logger.error(f"Failed to send daily report to {accountant.telegram_id}: {e}")

def get_vehicles_with_wash_reports(days: int = 30) -> list:
    """Машины, у которых есть фото мойки за последние N дней."""
    cutoff = date.today() - timedelta(days=days)
    vehicles = Vehicle.objects.filter(
        wash_reports__created_at__date__gte=cutoff
    ).select_related('driver').distinct().order_by('number')
    return list(vehicles)

def get_wash_reports_for_vehicle(vehicle_id: int, days: int = 30) -> list:
    """Список отчётов о мойке для конкретной машины."""
    cutoff = date.today() - timedelta(days=days)
    reports = WashReport.objects.filter(
        vehicle_id=vehicle_id,
        created_at__date__gte=cutoff
    ).select_related('vehicle').order_by('-created_at')
    return list(reports)


def get_current_wash_violations():
    """Возвращает список текущих нарушений мойки (vehicle, days) без отправки."""
    cutoff = timezone.now() - timedelta(days=7)
    vehicles = Vehicle.objects.annotate(
        last_wash=Max('wash_reports__created_at')
    ).filter(
        last_wash__lt=cutoff
    ) | Vehicle.objects.filter(wash_reports__isnull=True)

    vehicles = vehicles.select_related('driver').distinct()
    violations = []
    for vehicle in vehicles:
        if vehicle.last_wash:
            days = (timezone.now() - vehicle.last_wash).days
        else:
            # Если дата создания водителя не хранится, можно заменить на 30
            days = (timezone.now() - vehicle.created_at).days if hasattr(vehicle, 'created_at') else 30
        violations.append((vehicle, days))
    return violations