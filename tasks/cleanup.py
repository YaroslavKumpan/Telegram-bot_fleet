from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from apps.reports.models import WashReport, ServiceReport

@shared_task(name='tasks.cleanup.cleanup_old_reports')
def cleanup_old_reports():
    one_year_ago = timezone.now() - timedelta(days=365)
    w, _ = WashReport.objects.filter(created_at__lt=one_year_ago).delete()
    s, _ = ServiceReport.objects.filter(created_at__lt=one_year_ago).delete()
    return f'Deleted {w} wash reports and {s} service reports'