from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.reports.models import ServiceReport
from apps.users.models import User

from collections import defaultdict
import logging

from services.notification_service import notify_accountants_daily_report

logger = logging.getLogger(__name__)


@shared_task(name='tasks.daily_report.send_daily_report')
def send_daily_report():
    """
    Ежедневная задача: собирает все акты за сегодня,
    группирует по водителям и отправляет бухгалтерам.
    """
    today = timezone.now().date()
    today_start = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.min.time())
    )
    today_end = today_start + timedelta(days=1)

    reports = ServiceReport.objects.filter(
        created_at__gte=today_start,
        created_at__lt=today_end
    ).select_related('vehicle', 'vehicle__driver').order_by('vehicle__driver', 'created_at')

    if not reports.exists():
        logger.info("No service reports today, skipping daily report")
        return 0

    # Группируем по водителям
    by_driver = defaultdict(list)
    for report in reports:
        by_driver[report.vehicle.driver].append(report)

    # Отправляем бухгалтерам
    notify_accountants_daily_report(by_driver, today)

    return len(reports)