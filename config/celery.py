import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('fleet_bot')

# Загружаем настройки из Django settings с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях
app.autodiscover_tasks()

# Расписание задач
app.conf.beat_schedule = {
    'check-washes-weekly': {
        'task': 'tasks.weekly.check_wash_reports',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Каждый понедельник в 9:00
    },
}