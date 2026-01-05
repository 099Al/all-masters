from aiogram.fsm.state import StatesGroup, State

class SearchSpecialistDialog(StatesGroup):
    category = State()
    service = State()
    specialists = State()