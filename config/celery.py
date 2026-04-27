# config/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('fleet_bot')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Форсируем загрузку модулей с задачами ПОСЛЕ django.setup()
import django
django.setup()

app.conf.beat_schedule = {
    'check-washes-weekly': {
        'task': 'tasks.weekly.check_wash_reports',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Пн 9:00
    },
    'send-daily-report': {
        'task': 'tasks.daily_report.send_daily_report',
        'schedule': crontab(hour=18, minute=0),  # Каждый день в 18:00
    },
}