import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('fleet_bot')
app.config_from_object('django.conf:settings', namespace='CELERY')

import django
django.setup()

# Импортируем задачи, чтобы Celery их зарегистрировал
from tasks.notifications import notify_accountants_task
from tasks.weekly import check_wash_reports
from tasks.cleanup import cleanup_old_reports
from tasks.mileage_reminder import remind_drivers

app.conf.beat_schedule = {
    'check-washes-weekly': {
        'task': 'tasks.weekly.check_wash_reports',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),
    },
    'cleanup-old-reports': {
        'task': 'tasks.cleanup.cleanup_old_reports',
        'schedule': crontab(day_of_month=1, hour=3, minute=0),
    },
    'remind-mileage-monthly': {
        'task': 'tasks.mileage_reminder.remind_drivers',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),
    },
}