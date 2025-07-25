from aiogram.fsm.state import StatesGroup, State

class CheckinDialog(StatesGroup):
    checkin_message = State()
    info_message = State()
    name = State()
    phone = State()
    email = State()
    telegram = State()
    specialty = State()
    about = State()
    photo = State()
    confirm = State()
    answer = State()

class EditDialog(StatesGroup):
    name = State()
    phone = State()
    email = State()
    telegram = State()
    specialty = State()
    about = State()
    photo = State()
    confirm = State()
    answer = State()