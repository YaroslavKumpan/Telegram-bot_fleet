from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Max
from apps.reports.models import Vehicle
from services.notification_service import notify_directors_about_violations
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_wash_reports():
    """
    Еженедельная проверка: ищем машины без мойки более 7 дней.
    Уведомляем директоров о нарушениях.
    """
    cutoff = timezone.now() - timedelta(days=7)

    # Машины, у которых последняя мойка была более 7 дней назад
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
            days = (timezone.now() - vehicle.created_at).days if hasattr(vehicle, 'created_at') else 30

        violations.append((vehicle, days))

    if violations:
        notify_directors_about_violations(violations)
        logger.info(f"Found {len(violations)} wash violations")
    else:
        logger.info("No wash violations found")

    return len(violations)