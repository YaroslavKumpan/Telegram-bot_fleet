from apps.users.models import User

# Синхронная версия (для использования в sync-контексте)
def get_user_by_telegram_id_sync(telegram_id: int):
    """Синхронная версия. Использовать ТОЛЬКО вне async-контекста."""
    try:
        return User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return None

def register_driver_sync(telegram_id: int, first_name: str, last_name: str = ''):
    """Синхронная регистрация водителя."""
    username = f"driver_{telegram_id}"
    user = User.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        telegram_id=telegram_id,
        role=User.Role.DRIVER
    )
    return user