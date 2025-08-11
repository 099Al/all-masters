from aiogram.fsm.state import StatesGroup, State

class CheckinDialog(StatesGroup):
    checkin_message = State()
    info_message = State()
    request_phone = State()
    email = State()
    name = State()
    services = State()
    about = State()
    photo = State()
    confirm = State()
    answer = State()

class EditDialog(StatesGroup):
    request_phone = State()
    email = State()
    name = State()
    services = State()
    about = State()
    photo = State()
    message_to_admin = State()
    confirm = State()
    answer = State()
