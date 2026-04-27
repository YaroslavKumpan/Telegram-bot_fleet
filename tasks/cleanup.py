from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.reports.models import WashReport, ServiceReport


@shared_task
def cleanup_old_reports():
    """Удаляет отчёты старше 1 года."""
    one_year_ago = timezone.now() - timedelta(days=365)
    deleted_wash, _ = WashReport.objects.filter(created_at__lt=one_year_ago).delete()
    deleted_service, _ = ServiceReport.objects.filter(created_at__lt=one_year_ago).delete()
    return f"Deleted {deleted_wash} wash reports and {deleted_service} service reports"