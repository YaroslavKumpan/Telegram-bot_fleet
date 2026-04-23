from aiogram.fsm.state import StatesGroup, State

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_vehicle_number = State()