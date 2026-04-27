from celery import shared_task
from services.notification_service import notify_accountants_about_report


@shared_task(name='tasks.notifications.notify_accountants_task', bind=True, max_retries=3, default_retry_delay=60)
def notify_accountants_task(self, report_id: int):
    """
    Задача Celery для отправки уведомлений бухгалтерам.
    Вызывается из services.report_service после сохранения акта.
    """
    try:
        notify_accountants_about_report(report_id)
    except Exception as exc:
        raise self.retry(exc=exc)