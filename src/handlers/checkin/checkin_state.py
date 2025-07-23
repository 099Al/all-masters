from aiogram.fsm.state import StatesGroup, State

class CheckinDialog(StatesGroup):
    offer_message = State()
    info_message = State()
    name = State()
    phone = State()
    email = State()
    specialty = State()
    about = State()
    photo = State()
    confirm = State()
    answer = State()

class UpdateDialog(StatesGroup):
    name = State()
    phone = State()
    email = State()
    specialty = State()
    about = State()
    photo = State()
    confirm = State()
    answer = State()