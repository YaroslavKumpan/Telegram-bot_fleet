from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from asgiref.sync import sync_to_async

from bot.filters.filters import RoleFilter
from bot.keyboards.accountant import vehicles_list_keyboard
from bot.keyboards.default import main_menu_keyboard
from services.accountant_service import (
    get_all_vehicles_with_reports,
    get_service_reports_for_vehicle,
    get_vehicle_by_id,
    format_report_list
)
from services.notification_service import (
    get_current_wash_violations,
    get_vehicles_with_wash_reports,
    get_wash_reports_for_vehicle
)
from services.vehicle_service import format_vehicle_number

router = Router()

# ---------- 📸 Фотоотчёты мойки ----------

@router.message(F.text == "📸 Фотоотчёты мойки", RoleFilter("director"))
async def director_wash_photos(message: Message):
    vehicles = await sync_to_async(get_vehicles_with_wash_reports)(days=30)
    if not vehicles:
        await message.answer("📸 За последние 30 дней нет фото мойки.", reply_markup=main_menu_keyboard('director'))
        return

    await message.answer(
        "📸 <b>Фотоотчёты мойки за 30 дней</b>\n\nВыберите машину:",
        reply_markup=vehicles_list_keyboard(vehicles, "director_wash", use_accountant_prefix=False)
    )


@router.callback_query(F.data.startswith("director_wash_"))
async def show_wash_reports(callback: CallbackQuery):
    try:
        vehicle_id = int(callback.data.split("_")[-1])
        vehicle = await sync_to_async(get_vehicle_by_id)(vehicle_id)
        if not vehicle:
            await callback.answer("Машина не найдена", show_alert=True)
            return

        reports = await sync_to_async(get_wash_reports_for_vehicle)(vehicle_id, days=30)
        if not reports:
            await callback.message.edit_text("Нет фото мойки за этот период.")
            await callback.answer()
            return

        text = f"🚗 <b>{format_vehicle_number(vehicle.number)}</b> — {vehicle.driver.full_name}\n"
        text += f"Найдено фото: {len(reports)}\n\nВыберите дату:"

        buttons = []
        for rep in reports:
            date_str = rep.created_at.strftime('%d.%m %H:%M')
            buttons.append([InlineKeyboardButton(text=f"📷 {date_str}", callback_data=f"show_wash_{rep.id}")])
        buttons.append([InlineKeyboardButton(text="🔙 К списку машин", callback_data="back_to_director_wash_list")])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error in show_wash_reports: {e}", exc_info=True)
        await callback.answer("Произошла ошибка. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data.startswith("show_wash_"))
async def show_wash_photo(callback: CallbackQuery):
    report_id = int(callback.data.split("_")[-1])
    from apps.reports.models import WashReport

    report = await sync_to_async(WashReport.objects.select_related('vehicle').get)(id=report_id)
    if not report.photo:
        await callback.answer("Фото отсутствует", show_alert=True)
        return

    photo = FSInputFile(report.photo.path)
    caption = f"🧽 Мойка {format_vehicle_number(report.vehicle.number)}\n{report.created_at.strftime('%d.%m.%Y %H:%M')}"
    await callback.message.answer_photo(photo=photo, caption=caption)
    await callback.answer("Фото отправлено")


@router.callback_query(F.data == "back_to_director_wash_list")
async def back_to_wash_list(callback: CallbackQuery):
    vehicles = await sync_to_async(get_vehicles_with_wash_reports)(days=30)
    if not vehicles:
        await callback.message.edit_text("📸 Фото мойки за 30 дней не найдены.")
        return
    await callback.message.edit_text(
        "📸 <b>Фотоотчёты мойки за 30 дней</b>\n\nВыберите машину:",
        reply_markup=vehicles_list_keyboard(vehicles, "director_wash", use_accountant_prefix=False)
    )
    await callback.answer()


# ---------- 📋 Акты работ ----------

@router.message(F.text == "📋 Акты работ", RoleFilter("director"))
async def director_acts(message: Message):
    vehicles = await sync_to_async(get_all_vehicles_with_reports)(days=30)
    if not vehicles:
        await message.answer("📋 За последние 30 дней актов нет.", reply_markup=main_menu_keyboard('director'))
        return
    await message.answer(
        "📋 <b>Акты работ за 30 дней</b>\n\nВыберите машину:",
        reply_markup=vehicles_list_keyboard(vehicles, "director_acts", use_accountant_prefix=False)
    )


@router.callback_query(F.data.startswith("director_acts_"))
async def show_vehicle_acts(callback: CallbackQuery):
    vehicle_id = int(callback.data.split("_")[-1])
    vehicle = await sync_to_async(get_vehicle_by_id)(vehicle_id)
    if not vehicle:
        await callback.answer("Машина не найдена", show_alert=True)
        return

    reports = await sync_to_async(get_service_reports_for_vehicle)(vehicle_id, days=30)
    text = format_report_list(vehicle, reports, days=30)

    buttons = []
    for report in reports[:5]:
        date_str = report.created_at.strftime('%d.%m %H:%M')
        buttons.append([InlineKeyboardButton(text=f"📄 {date_str}", callback_data=f"director_show_act_{report.id}")])
    buttons.append([InlineKeyboardButton(text="🔙 К списку машин", callback_data="back_to_director_acts")])

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data == "back_to_director_acts")
async def back_to_acts_list(callback: CallbackQuery):
    vehicles = await sync_to_async(get_all_vehicles_with_reports)(days=30)
    if not vehicles:
        await callback.message.edit_text("📋 Актов за 30 дней нет.")
        return
    await callback.message.edit_text(
        "📋 <b>Акты работ за 30 дней</b>\n\nВыберите машину:",
        reply_markup=vehicles_list_keyboard(vehicles, "director_acts", use_accountant_prefix=False)
    )
    await callback.answer()


# Детали акта и фото с уникальными префиксами
@router.callback_query(F.data.startswith("director_show_act_"))
async def show_act_detail(callback: CallbackQuery):
    report_id = int(callback.data.split("_")[-1])
    from apps.reports.models import ServiceReport
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
        buttons.append([InlineKeyboardButton(text="📸 Открыть фото", callback_data=f"director_view_photo_{report.id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад к актам", callback_data=f"director_acts_{report.vehicle.id}")])

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("director_view_photo_"))
async def view_act_photo(callback: CallbackQuery):
    report_id = int(callback.data.split("_")[-1])
    from apps.reports.models import ServiceReport
    report = await sync_to_async(ServiceReport.objects.get)(id=report_id)
    if report.photo:
        photo = FSInputFile(report.photo.path)
        await callback.message.answer_photo(photo=photo, caption=f"Акт от {report.created_at.strftime('%d.%m.%Y %H:%M')}")
        await callback.answer("Фото отправлено")
    else:
        await callback.answer("Фото отсутствует", show_alert=True)


# ---------- ⚠️ Нарушения мойки ----------
@router.message(F.text == "⚠️ Нарушения мойки", RoleFilter("director"))
async def director_violations(message: Message):
    violations = await sync_to_async(get_current_wash_violations)()
    if not violations:
        await message.answer("✅ Все машины помыты вовремя!", reply_markup=main_menu_keyboard('director'))
        return

    text = "⚠️ <b>Текущие нарушения графика мойки</b>\n\n"
    from collections import defaultdict
    by_driver = defaultdict(list)
    for vehicle, days in violations:
        by_driver[vehicle.driver].append((vehicle, days))

    for driver, lst in by_driver.items():
        text += f"👤 <b>{driver.full_name}</b>:\n"
        for vehicle, days in lst:
            text += f"  • {format_vehicle_number(vehicle.number)} — {days} дн. без мойки\n"
        text += "\n"

    await message.answer(text, reply_markup=main_menu_keyboard('director'))