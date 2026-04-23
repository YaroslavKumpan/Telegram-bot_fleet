from apps.vehicles.models import Vehicle
from apps.users.models import User
import re


def normalize_vehicle_number(number: str) -> str:
    """
    Приводит номер к единому формату хранения.
    Поддерживает белорусские форматы:
    - 1234 AB-7 (новый образец, легковые)
    - AB 1234-7 (новый образец, альтернативная запись)
    - А123ВС (старый образец)
    - АТ9288-7 (старый образец с регионом)

    Всегда сохраняем в формате: БУКВЫ ЦИФРЫ-РЕГИОН (без пробелов)
    Например: AT9288-7, AB1234-7, A123BC-7
    """
    number = number.strip().upper()

    # Убираем все пробелы
    number = ''.join(number.split())

    # Если номер в формате "1234AB-7" (цифры потом буквы) -> "AB1234-7"
    match = re.match(r'^(\d{4})([A-ZА-Я]{2})-(\d)$', number)
    if match:
        digits, letters, region = match.groups()
        # Конвертируем кириллицу в латиницу
        letters = transliterate_cyrillic_to_latin(letters)
        return f"{letters}{digits}-{region}"

    # Если номер уже в формате "AB1234-7" или "A123BC-7" или "AT9288-7"
    match = re.match(r'^([A-ZА-Я]{1,2})(\d{4})-(\d)$', number)
    if match:
        letters, digits, region = match.groups()
        letters = transliterate_cyrillic_to_latin(letters)
        return f"{letters}{digits}-{region}"

    # Старый формат без региона: А123ВС -> A123BC
    match = re.match(r'^([A-ZА-Я])(\d{3})([A-ZА-Я]{2})$', number)
    if match:
        letter1, digits, letters2 = match.groups()
        letter1 = transliterate_cyrillic_to_latin(letter1)
        letters2 = transliterate_cyrillic_to_latin(letters2)
        return f"{letter1}{digits}{letters2}"

    # Если не удалось нормализовать - возвращаем как есть
    return number


def transliterate_cyrillic_to_latin(text: str) -> str:
    """
    Транслитерация кириллических символов номера в латиницу.
    Актуально для белорусских номеров, где используются буквы А, В, Е, І, К, М, Н, О, Р, С, Т, Х
    """
    mapping = {
        'А': 'A', 'В': 'B', 'Е': 'E', 'І': 'I', 'К': 'K',
        'М': 'M', 'Н': 'H', 'О': 'O', 'Р': 'P', 'С': 'C',
        'Т': 'T', 'Х': 'X', 'У': 'Y',
    }
    return ''.join(mapping.get(c, c) for c in text)


def format_vehicle_number(number: str) -> str:
    """
    Форматирует номер для отображения.
    AB1234-7 -> AB 1234-7
    AT9288-7 -> AT 9288-7
    A123BC -> A 123 BC
    """
    number = number.strip().upper()

    # AB1234-7 -> AB 1234-7
    match = re.match(r'^([A-Z]{2})(\d{4})-(\d)$', number)
    if match:
        return f"{match.group(1)} {match.group(2)}-{match.group(3)}"

    # A1234-7 (одна буква, 4 цифры, регион)
    match = re.match(r'^([A-Z])(\d{4})-(\d)$', number)
    if match:
        return f"{match.group(1)} {match.group(2)}-{match.group(3)}"

    # AT9288-7 -> AT 9288-7
    match = re.match(r'^([A-Z]{2})(\d{4})-(\d)$', number)
    if match:
        return f"{match.group(1)} {match.group(2)}-{match.group(3)}"

    # A123BC -> A 123 BC
    match = re.match(r'^([A-Z])(\d{3})([A-Z]{2})$', number)
    if match:
        return f"{match.group(1)} {match.group(2)} {match.group(3)}"

    return number


def validate_vehicle_number(number: str) -> bool:
    """
    Валидация белорусских госномеров.
    Поддерживает форматы:
    - 1234 AB-7 (новый, легковые)
    - AB 1234-7 (новый, альтернатива)
    - А123ВС (старый)
    - А123ВС-7 (старый с регионом)
    """
    cleaned = number.strip().upper()
    cleaned = ''.join(cleaned.split())  # убираем пробелы

    # Проверка длины
    if len(cleaned) < 6 or len(cleaned) > 8:
        return False

    # Проверяем форматы
    patterns = [
        # 1234AB-7 (новый: 4 цифры, 2 буквы, регион)
        r'^\d{4}[A-ZА-Я]{2}-\d$',
        # AB1234-7 (новый альтернативный: 2 буквы, 4 цифры, регион)
        r'^[A-ZА-Я]{2}\d{4}-\d$',
        # A123BC (старый: буква, 3 цифры, 2 буквы)
        r'^[A-ZА-Я]\d{3}[A-ZА-Я]{2}$',
        # A123BC-7 (старый с регионом: буква, 3 цифры, 2 буквы, регион)
        r'^[A-ZА-Я]\d{3}[A-ZА-Я]{2}-\d$',
    ]

    return any(re.match(pattern, cleaned) for pattern in patterns)


def add_vehicle_for_user_sync(user_id: int, number: str) -> tuple:
    """
    Добавляет машину водителю.
    Возвращает (успех, сообщение, Vehicle/None)
    """
    # Нормализуем номер для хранения
    normalized_number = normalize_vehicle_number(number)

    # Валидация
    if not validate_vehicle_number(number):
        return False, (
            "❌ Некорректный формат госномера.\n\n"
            "Поддерживаемые форматы:\n"
            "• 1234 AB-7 (новый образец)\n"
            "• AB 1234-7 (новый образец)\n"
            "• А123ВС (старый образец)\n"
            "• А123ВС-7 (старый с регионом)\n\n"
            "Попробуйте ещё раз:"
        ), None

    # Проверяем уникальность
    if Vehicle.objects.filter(number=normalized_number).exists():
        return False, f"❌ Машина с номером {format_vehicle_number(normalized_number)} уже зарегистрирована в системе.", None

    try:
        user = User.objects.get(telegram_id=user_id)
    except User.DoesNotExist:
        return False, "❌ Пользователь не найден. Используйте /start", None

    # Создаём машину
    vehicle = Vehicle.objects.create(
        number=normalized_number,
        driver=user
    )

    display_number = format_vehicle_number(normalized_number)
    return True, f"✅ Машина {display_number} успешно добавлена!", vehicle


def get_user_vehicles_sync(telegram_id: int) -> list:
    """
    Получает список машин пользователя.
    Возвращает список Vehicle с отформатированными номерами.
    """
    try:
        user = User.objects.get(telegram_id=telegram_id)
        vehicles = list(user.vehicles.all())
        return vehicles
    except User.DoesNotExist:
        return []