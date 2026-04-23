from apps.users.models import User

def process_invite(telegram_id: int, invite_code: str) -> tuple[bool, str]:
    """
    Обрабатывает инвайт-код при запуске бота.
    Возвращает кортеж (успех, сообщение).
    """
    # Ищем пользователя с таким invite_code и без telegram_id
    try:
        user = User.objects.get(invite_code=invite_code, telegram_id__isnull=True)
    except User.DoesNotExist:
        return False, "❌ Неверный или уже использованный код приглашения."

    # Проверяем, что этот telegram_id ещё не привязан к другому пользователю
    if User.objects.filter(telegram_id=telegram_id).exists():
        return False, "❌ Этот Telegram аккаунт уже привязан к другому пользователю."

    # Привязываем пользователя и очищаем код
    user.telegram_id = telegram_id
    user.invite_code = None
    user.save()

    role_display = user.get_role_display()
    return True, f"✅ Вы успешно подключены как {role_display}!"