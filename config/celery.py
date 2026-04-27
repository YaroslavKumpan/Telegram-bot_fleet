# config/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('fleet_bot')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Сначала загружаем Django
import django
django.setup()

# Теперь импортируем задачи – они автоматически регистрируются в Celery
from tasks.notifications import notify_accountants_task
from tasks.weekly import check_wash_reports
from tasks.daily_report import send_daily_report

app.conf.beat_schedule = {
    'check-washes-weekly': {
        'task': 'tasks.weekly.check_wash_reports',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),
    },
    'send-daily-report': {
        'task': 'tasks.daily_report.send_daily_report',
        'schedule': crontab(hour=18, minute=0),
    },
    'cleanup-old-reports': {
    'task': 'tasks.cleanup.cleanup_old_reports',
    'schedule': crontab(day_of_month=1, hour=3, minute=0),  # 1 числа каждого месяца в 3 утра
    },
}