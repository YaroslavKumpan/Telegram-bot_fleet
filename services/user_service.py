from apps.users.models import User

def get_user_by_telegram_id(telegram_id: int) -> User | None:
    """Получает пользователя по telegram_id."""
    try:
        return User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return None

def register_driver(telegram_id: int, first_name: str, last_name: str = '') -> User:
    """Регистрирует нового водителя через бота."""
    username = f"driver_{telegram_id}"
    user = User.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        telegram_id=telegram_id,
        role=User.Role.DRIVER
    )
    return user