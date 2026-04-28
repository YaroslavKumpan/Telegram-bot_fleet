from aiogram.fsm.state import StatesGroup, State

class MileageStates(StatesGroup):
    waiting_for_value = State()