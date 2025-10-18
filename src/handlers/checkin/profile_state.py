from aiogram.fsm.state import StatesGroup, State

class CheckinUserDialog(StatesGroup):
    checkin_message = State()
    ban_message = State()
    checkin_service_rules = State()
    request_phone = State()
    checkin_user_done = State()


class CheckinDialog(StatesGroup):
    checkin_message = State()
    info_message = State()
    #request_phone = State()
    name = State()
    email = State()
    services = State()
    about = State()
    photo = State()
    photo_works = State()
    photo_works_another = State()
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
