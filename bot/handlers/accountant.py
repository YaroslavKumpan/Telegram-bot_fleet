from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

from bot.filters.filters import RoleFilter
from services.user_service import get_user_by_telegram_id_sync
from services.accountant_service import (
    get_all_vehicles_with_reports,
    get_service_reports_for_vehicle,
    get_vehicle_by_id,
    format_report_list
)
from services.vehicle_service import format_vehicle_number
from bot.keyboards.default import main_menu_keyboard
from bot.keyboards.accountant import vehicles_list_keyboard
from aiogram.types import FSInputFile
from services.mileage_service import get_all_mileages_sync, get_vehicles_without_mileage_sync

router = Router()


@router.message(F.text == "📋 Акты работ", RoleFilter("accountant"))
async def show_acts_menu(message: Message):
    user = await sync_to_async(get_user_by_telegram_id_sync)(message.from_user.id)
    if not user or user.role != 'accountant':
        return

    # Возвращается список, "if not vehicles" безопасен
    vehicles = await sync_to_async(get_all_vehicles_with_reports)(days=30)

    if not vehicles:
        await message.answer(
            "📋 За последние 30 дней актов нет.",
            reply_markup=main_menu_keyboard(user.role)
        )
        return

    await message.answer(
        "📋 <b>Акты работ за 30 дней</b>\n\nВыберите машину:",
        reply_markup=vehicles_list_keyboard(vehicles, "acts")
    )


# Обработчик выбора машины
@router.callback_query(F.data.startswith("accountant_acts_"))
async def show_vehicle_acts(callback: CallbackQuery):
    vehicle_id = int(callback.data.split("_")[-1])

    vehicle = await sync_to_async(get_vehicle_by_id)(vehicle_id)
    if not vehicle:
        await callback.answer("Машина не найдена", show_alert=True)
        return

    reports = await sync_to_async(get_service_reports_for_vehicle)(vehicle_id, days=30)
    text = format_report_list(vehicle, reports, days=30)  # Синхронно, без БД

    # Кнопки для каждого акта (последние 5)
    buttons = []
    for report in reports[:5]:
        date_str = report.created_at.strftime('%d.%m %H:%M')
        buttons.append([
            InlineKeyboardButton(
                text=f"📄 {date_str}",
                callback_data=f"show_act_{report.id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 К списку машин", callback_data="back_to_acts_list")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


# Просмотр деталей акта
@router.callback_query(F.data.startswith("show_act_"))
async def show_act_detail(callback: CallbackQuery):
    report_id = int(callback.data.split("_")[-1])
    from apps.reports.models import ServiceReport

    # Получение отчёта синхронно через sync_to_async
    report = await sync_to_async(ServiceReport.objects.select_related('vehicle', 'vehicle__driver').get)(id=report_id)

    vehicle_number = format_vehicle_number(report.vehicle.number)
    driver_name = report.vehicle.driver.full_name
    date_str = report.created_at.strftime('%d.%m.%Y %H:%M')

    text = (
        f"🧾 <b>Акт выполненных работ</b>\n\n"
        f"🚗 Машина: {vehicle_number}\n"
        f"👤 Водитель: {driver_name}\n"
        f"📅 Дата: {date_str}\n"
        f"📸 Фото: {'есть' if report.photo else 'отсутствует'}"
    )

    buttons = []
    if report.photo:
        buttons.append([InlineKeyboardButton(text="📸 Открыть фото", callback_data=f"view_photo_{report.id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад к актам", callback_data=f"accountant_acts_{report.vehicle.id}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


# Возврат к списку машин
@router.callback_query(F.data == "back_to_acts_list")
async def back_to_acts_list(callback: CallbackQuery):
    vehicles = await sync_to_async(get_all_vehicles_with_reports)(days=30)
    if not vehicles:
        await callback.message.edit_text("📋 Актов за 30 дней нет.")
        return
    await callback.message.edit_text(
        "📋 <b>Акты работ за 30 дней</b>\n\nВыберите машину:",
        reply_markup=vehicles_list_keyboard(vehicles, "acts")
    )
    await callback.answer()


# Просмотр фото
@router.callback_query(F.data.startswith("view_photo_"))
async def view_act_photo(callback: CallbackQuery):
    report_id = int(callback.data.split("_")[-1])
    from apps.reports.models import ServiceReport

    report = await sync_to_async(
        ServiceReport.objects.select_related('vehicle', 'vehicle__driver').get
    )(id=report_id)

    if report.photo:
        try:
            # Отправляем как локальный файл
            photo_file = FSInputFile(report.photo.path)
            await callback.message.answer_photo(
                photo=photo_file,
                caption=f"Акт от {report.created_at.strftime('%d.%m.%Y %H:%M')}"
            )
            await callback.answer("Фото отправлено")
        except Exception as e:
            await callback.answer(f"Ошибка отправки фото: {e}", show_alert=True)
    else:
        await callback.answer("Фото отсутствует", show_alert=True)

@router.message(F.text == "🛣 Пробеги", RoleFilter("accountant"))
async def show_mileage(message: Message):
    mileages = await sync_to_async(get_all_mileages_sync)()
    without = await sync_to_async(get_vehicles_without_mileage_sync)()

    if not mileages and not without:
        await message.answer("Нет данных о пробегах.", reply_markup=main_menu_keyboard('accountant'))
        return

    text = "🛣 <b>Пробеги машин</b>\n\n"

    if mileages:
        for m in mileages:
            text += (
                f"🚗 {m['vehicle_number']} — <b>{m['value']:,} км</b>\n"
                f"   👤 {m['driver_name']} | 📅 {m['updated_at'].strftime('%d.%m.%Y')}\n\n"
            ).replace(",", " ")  # убираем запятые в числе

    if without:
        text += "⚠️ <b>Нет данных:</b>\n"
        for v in without:
            text += f"• {format_vehicle_number(v.number)} ({v.driver.full_name})\n"

    await message.answer(text, reply_markup=main_menu_keyboard('accountant'))