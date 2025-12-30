from datetime import datetime

from aiogram.types import ContentType
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Back, Next, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import RequestContact
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput

from src.config_paramaters import configs
from src.database.models import Users
from src.database.requests_db import ReqData
from src.handlers.checkin.profile_state import CheckinDialog, CheckinUserDialog
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory

from src.handlers.menu.start.start_state import StartDialog
from src.config import settings

import src.log_settings
import logging
logger = logging.getLogger(__name__)


async def checkin_out(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()

window_user_checkin_ban = Window(
                Format("Вы забанены за нарушение правил сервиса"),
                Button(Const("Выйти"), id="chekin_user_out", on_click=checkin_out),
                state=CheckinUserDialog.ban_message,
)



async def start_checkin(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(CheckinUserDialog.checkin_service_rules)


window_user_checkin_start = Window(
                Format("Зарегистрируйтесь \nдля использования сервиса"),

                Button(Const("Зарегистрироваться"), id="id_registration_user_start", on_click=start_checkin),
                state=CheckinUserDialog.checkin_message,
)


async def reg_user_confirm(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(CheckinUserDialog.request_phone)

window_user_checkin_rules = Window(
                Format("Ознакомтесь с условиями использования сервиса"),
                    Url(text=Format("Пользовательское соглашение"), url=Const(f"{settings.base_url_https}/message/rules")),
                    Button(Const("Соглашаюсь"), id="id_registration_user_confirm", on_click=reg_user_confirm),
                    state=CheckinUserDialog.checkin_service_rules,
)


async def contact_message(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    phone = message.contact.phone_number
    tg = message.from_user.username

    user = Users(
        id=message.from_user.id,
        phone=phone,
        telegram=tg,
        created_at=datetime.now(configs.UTC_PLUS_5).replace(tzinfo=None),
    )

    req = ReqData()
    await req.save_profile_data(user)

    await dialog_manager.switch_to(CheckinUserDialog.checkin_user_done)

window_user_checkin_phone = Window(
                Format("Для регистрации нужен ваш телефон"),
                RequestContact(Const("Отправить контакт")),
                Back(Const("Назад"), id="back"),
                MessageInput(contact_message, ContentType.CONTACT),
                markup_factory=ReplyKeyboardFactory(
                            input_field_placeholder=Format("{event.from_user.username}"),
                            resize_keyboard=True,
                            one_time_keyboard=True
                            ),
                state=CheckinUserDialog.request_phone,
)


async def start_service(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await dialog_manager.start(StartDialog.start, mode=StartMode.RESET_STACK)

window_user_checkin_done = Window(
                Format("Вы зарегестированы"),
                    Button(Const("Перейти к сервису"), id="id_start_service", on_click=start_service),
                    state=CheckinUserDialog.checkin_user_done,
)
