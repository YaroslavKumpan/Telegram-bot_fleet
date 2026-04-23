from apps.users.models import User

def process_invite_sync(telegram_id: int, invite_code: str) -> tuple:
    """
    Обрабатывает инвайт-код.
    Возвращает кортеж (успех, сообщение).
    """
    try:
        user = User.objects.get(invite_code=invite_code, telegram_id__isnull=True)
    except User.DoesNotExist:
        return False, "❌ Неверный или уже использованный код приглашения."

    if User.objects.filter(telegram_id=telegram_id).exists():
        return False, "❌ Этот Telegram аккаунт уже привязан к другому пользователю."

    user.telegram_id = telegram_id
    user.invite_code = None
    user.save()

    role_display = user.get_role_display()
    return True, f"✅ Вы успешно подключены как {role_display}!"