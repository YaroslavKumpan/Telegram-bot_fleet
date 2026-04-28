from apps.reports.models import Mileage
from apps.users.models import User
from apps.vehicles.models import Vehicle
from services.vehicle_service import format_vehicle_number


def update_mileage_sync(vehicle_id: int, value: int, user_id: int) -> tuple:
    """Обновляет пробег для машины. Возвращает (успех, сообщение)."""
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        user = User.objects.get(telegram_id=user_id)
    except Vehicle.DoesNotExist:
        return False, "❌ Машина не найдена."
    except User.DoesNotExist:
        return False, "❌ Пользователь не найден."

    if value <= 0:
        return False, "❌ Пробег должен быть больше нуля."

    mileage, created = Mileage.objects.update_or_create(
        vehicle=vehicle,
        defaults={
            'value': value,
            'updated_by': user,
        }
    )

    action = "обновлён" if not created else "сохранён"
    return True, f"✅ Пробег {format_vehicle_number(vehicle.number)} {action}: {value} км"


def get_all_mileages_sync() -> list:
    """Возвращает список всех пробегов с информацией о машинах и водителях."""
    mileages = Mileage.objects.select_related(
        'vehicle', 'vehicle__driver', 'updated_by'
    ).order_by('vehicle__number')

    result = []
    for m in mileages:
        result.append({
            'vehicle_number': format_vehicle_number(m.vehicle.number),
            'driver_name': m.vehicle.driver.full_name,
            'value': m.value,
            'updated_at': m.updated_at,
            'updated_by': m.updated_by.full_name if m.updated_by else '—',
        })
    return result


def get_vehicles_without_mileage_sync() -> list:
    """Машины, для которых ещё нет записи о пробеге."""
    vehicles_with_mileage = Mileage.objects.values_list('vehicle_id', flat=True)
    vehicles = Vehicle.objects.exclude(id__in=vehicles_with_mileage).select_related('driver')
    return list(vehicles)