# services/accountant_service.py
from datetime import date, timedelta
from apps.reports.models import ServiceReport
from apps.vehicles.models import Vehicle
from services.vehicle_service import format_vehicle_number


def get_all_vehicles_with_reports(days: int = 30) -> list:
    """
    Возвращает список машин, у которых есть акты за последние N дней.
    Результат — готовый список объектов Vehicle (с водителями).
    """
    cutoff = date.today() - timedelta(days=days)
    vehicles = Vehicle.objects.filter(
        service_reports__created_at__date__gte=cutoff
    ).select_related('driver').distinct().order_by('number')
    # Преобразуем в список, чтобы избежать ленивых обращений в async-контексте
    return list(vehicles)


def get_service_reports_for_vehicle(vehicle_id: int, days: int = 30) -> list:
    """
    Возвращает список актов для конкретной машины за последние N дней.
    """
    cutoff = date.today() - timedelta(days=days)
    reports = ServiceReport.objects.filter(
        vehicle_id=vehicle_id,
        created_at__date__gte=cutoff
    ).select_related('vehicle', 'vehicle__driver').order_by('-created_at')
    return list(reports)


def get_vehicle_by_id(vehicle_id: int):
    """
    Возвращает объект Vehicle или None.
    """
    try:
        return Vehicle.objects.select_related('driver').get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return None


def format_report_list(vehicle, reports, days=30) -> str:
    """
    Форматирует список актов для отображения (синхронно, без запросов к БД).
    """
    vehicle_number = format_vehicle_number(vehicle.number)
    driver_name = vehicle.driver.full_name

    text = f"🚗 <b>{vehicle_number}</b>\n"
    text += f"👤 Водитель: {driver_name}\n"
    text += f"📅 Акты за {days} дней: {len(reports)} шт.\n\n"

    if reports:
        text += "<b>Последние акты:</b>\n\n"
        for i, report in enumerate(reports, 1):
            date_str = report.created_at.strftime('%d.%m.%Y %H:%M')
            has_photo = "📸" if report.photo else "❌"
            text += f"{i}. {date_str} {has_photo}\n"
    else:
        text += "Актов за выбранный период нет."

    return text