from aiogram.fsm.state import StatesGroup, State

class ReportStates(StatesGroup):
    waiting_for_wash_photo = State()
    waiting_for_service_photo = State()
    waiting_for_vehicle_number = State()  # для добавления машины