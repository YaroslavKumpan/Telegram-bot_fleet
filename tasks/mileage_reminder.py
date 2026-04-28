from celery import shared_task
from apps.users.models import User
from apps.vehicles.models import Vehicle
from infra.telegram_client import telegram_client
import logging

logger = logging.getLogger(__name__)

@shared_task(name='tasks.mileage_reminder.remind_drivers')
def remind_drivers():
    drivers = User.objects.filter(role=User.Role.DRIVER, telegram_id__isnull=False)
    count = 0

    for driver in drivers:
        vehicles = Vehicle.objects.filter(driver=driver)
        if not vehicles.exists():
            continue

        text = (
            "📅 <b>Наступил новый месяц!</b>\n\n"
            "🔔 Пожалуйста, отправьте текущий пробег вашей машины.\n\n"
            "Для этого нажмите кнопку:\n"
            "<b>«🛣 Отправить пробег»</b>\n\n"
            "Спасибо за своевременную подачу данных!"
        )

        try:
            telegram_client.send_message(driver.telegram_id, text)
            count += 1
        except Exception as e:
            logger.error(f"Reminder failed for {driver.telegram_id}: {e}")

    return f"Reminders sent to {count} drivers"