from aiogram.fsm.state import StatesGroup, State

class CheckinDialog(StatesGroup):
    checkin_message = State()
    info_message = State()
    request_phone = State()
    name = State()
    email = State()
    telegram = State()
    specialty = State()
    about = State()
    photo = State()
    confirm = State()
    answer = State()

class EditDialog(StatesGroup):
    request_phone = State()
    name = State()
    email = State()
    telegram = State()
    specialty = State()
    about = State()
    photo = State()
    confirm = State()
    answer = State()
