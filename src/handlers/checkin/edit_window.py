from datetime import datetime
import re
from urllib import request

from aiogram.fsm.context import FSMContext
from aiogram import Dispatcher, Bot, F
from aiogram.types import ContentType
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Back, Next, Cancel, RequestContact
from aiogram_dialog.widgets.text import Format, Const, List
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory

from src.config import settings
from src.config_paramaters import UTC_PLUS_5
from src.database.models import Specialist, UserStatus, ModerateData, ModerateStatus, UserModerateResult, ModerateLog
from src.database.requests_db import ReqData
from src.handlers.checkin.profile_state import CheckinDialog, EditDialog
from aiogram.types import CallbackQuery

from src.log_config import *
logger = logging.getLogger(__name__)





async def getter_edit_name(dialog_manager: DialogManager, **kwargs):
    user_data = dialog_manager.start_data
    return {"name": user_data['name']}

async def edit_name(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['name'] = message.text
    await dialog_manager.switch_to(EditDialog.request_phone)

def validate_name(name: str) -> str:
    invalid_char_pattern = r'[0-9!@#$%^&*_+=\[\]{};:"\\|,.<>\/?]'
    if re.search(invalid_char_pattern, name):
        raise ValueError("Имя содержит недопустимые символы")
    elif len(name) > 30:
        raise ValueError("Слишком длинное имя")
    else:
        return name

async def error_name(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    await message.answer(error.args[0])

window_edit_name = Window(
    Format("Ваше имя: {name}\nДля изменения введите новое значение"),
    TextInput(id="edit_name",
              type_factory=validate_name,
              on_success=edit_name,
              on_error=error_name
              ),
    Cancel(Const("🔙 Назад"), id="exit_edit"),
    Next(Const("⏩ Пропустить"), id="skip"),
    state=EditDialog.name,
    getter=getter_edit_name
)


async def contact_request(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data['phone'] = message.contact.phone_number
    dialog_manager.dialog_data['telegram'] = message.from_user.username
    await dialog_manager.switch_to(EditDialog.email)

async def getter_edit_phone(dialog_manager: DialogManager, **kwargs):
    user_data = dialog_manager.start_data
    return {"phone": user_data['phone']}

window_edit_phone = Window(
                Format("Ваш телефон: {phone}\nДля изменения телефона нужно отправить ваш контакт"),
                RequestContact(Const("Отправить контакт")),
                Back(Const("🔙 Назад"), id="back"),
                Next(Const("⏩ Пропустить"), id="skip"),
                MessageInput(contact_request, ContentType.CONTACT),
                markup_factory=ReplyKeyboardFactory(
                            input_field_placeholder=Format("{event.from_user.username}"),
                            resize_keyboard=True,
                            one_time_keyboard=True
                            ),
                state=EditDialog.request_phone,
                getter=getter_edit_phone
)


async def getter_edit_email(dialog_manager: DialogManager, **kwargs):
    user_data = dialog_manager.start_data
    return {"email": user_data['email']}

async def edit_email(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['email'] = message.text
    await dialog_manager.switch_to(EditDialog.specialty)


def validate_email(email: str) -> str:
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if len(email) > 50:
        raise ValueError("Слишком длинный email")
    elif not re.match(email_regex, email):
        raise ValueError("Invalid email address")
    else:
        return email

async def error_email(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    await message.answer("Некорректный email")


window_edit_email = Window(
    Format("Ваш email: {email}\nДля изменения введите новое значение"),
    TextInput(id="edit_email",
              type_factory=validate_email,
              on_success=edit_email,
              on_error=error_email
              ),
    Back(Const("🔙 Назад"), id="back_edit_email"),
    Next(Const("⏩ Пропустить"), id="skip"),
    state=EditDialog.email,
    getter=getter_edit_email
)


async def getter_edit_specialty(dialog_manager: DialogManager, **kwargs):
    user_data = dialog_manager.start_data
    return {"specialty": user_data['specialty']}

async def edit_specialty(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['specialty'] = message.text
    await dialog_manager.switch_to(EditDialog.about)

window_edit_specialty = Window(
    Format("Ваша специальность: {specialty}\nДля изменения введите новое значение"),
    TextInput(id="edit_specialty",
              type_factory=str,
              on_success=edit_specialty,
              ),
    Back(Const("🔙 Назад"), id="back_edit_specialty"),
    Next(Const("⏩ Пропустить"), id="skip"),
    state=EditDialog.specialty,
    getter=getter_edit_specialty
)


async def getter_edit_about(dialog_manager: DialogManager, **kwargs):
    user_data = dialog_manager.start_data
    return {"about": user_data['about']}

async def edit_about(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['about'] = message.text
    await dialog_manager.switch_to(EditDialog.photo)

window_edit_about = Window(
    Format("О себе: {about}\nДля изменения введите новое значение"),
    TextInput(id="edit_about",
              type_factory=str,
              on_success=edit_about,
              ),
    Back(Const("🔙 Назад"), id="back_edit_about"),
    Next(Const("⏩ Пропустить"), id="skip"),
    state=EditDialog.about,
    getter=getter_edit_about
)


async def getter_edit_photo(dialog_manager: DialogManager, **kwargs):
    user_data = dialog_manager.start_data
    return {}

async def edit_photo(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data['photo'] = message.photo[-1].file_id
    await dialog_manager.switch_to(EditDialog.confirm)

window_edit_photo = Window(
    Format("Для изменения загрузите новое фото"),
    MessageInput(id="edit_photo",
                 func=edit_photo,
                 content_types=ContentType.PHOTO
                 ),
    Back(Const("🔙 Назад"), id="back_edit_photo"),
    Next(Const("⏩ Пропустить"), id="skip"),
    state=EditDialog.photo,
    getter=getter_edit_photo
)


async def message_to_admin(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['message_to_admin'] = message.text
    await dialog_manager.switch_to(EditDialog.confirm)

def validate_message_to_admin(message_to_admin: str) -> str:
    if len(message_to_admin) > 700:
        raise ValueError("Слишком длинное сообщение")
    else:
        return message_to_admin

async def error_message_to_admin(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    await message.answer(error.args[0])

window_message_to_admin = Window(
    Format("Cообщение в службу поддержки (не более 700 символов)"),
    TextInput(id="message_to_admin",
              type_factory=validate_message_to_admin,
              on_success=message_to_admin,
              on_error=error_message_to_admin
              ),
    Back(Const("🔙 Назад"), id="back_message_to_admin"),
    Next(Const("⏩ Пропустить"), id="skip"),
    state=EditDialog.message_to_admin
)


async def edit_confirm(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    user_id = dialog_manager.start_data['user_id']
    img_telegram_id = dialog_manager.dialog_data.get('photo')
    local_path = f"{settings.NEW_IMAGES}/{user_id}.jpg"
    bot = callback.from_user.bot
    if img_telegram_id:
        await bot.download(img_telegram_id, destination=f"{settings.path_root}/{local_path}")
    else:
        local_path = None

    specialist_status = dialog_manager.start_data['status']

    #TODO: update Specialist moderate_result to NEW_CHANGES

    specialist_moderate = ModerateData(
        id=user_id,
        status=ModerateStatus.NEW_CHANGES,
        name=dialog_manager.dialog_data.get('name', dialog_manager.start_data['name']),
        phone=dialog_manager.dialog_data.get('phone', dialog_manager.start_data['phone']),
        telegram=dialog_manager.dialog_data.get('telegram', dialog_manager.start_data['telegram']),
        email=dialog_manager.dialog_data.get('email', dialog_manager.start_data['email']),
        specialty=dialog_manager.dialog_data.get('specialty', dialog_manager.start_data['specialty']),
        about=dialog_manager.dialog_data.get('about', dialog_manager.start_data['about']),
        photo_telegram=img_telegram_id,
        photo_local=local_path,
        updated_at=datetime.now(UTC_PLUS_5).replace(microsecond=0).replace(tzinfo=None),
        message_to_admin=dialog_manager.dialog_data.get('message_to_admin')
    )

    req = ReqData()
    await req.merge_profile_data(specialist_moderate)
    await req.update_specialist(user_id, moderate_result=UserModerateResult.NEW_CHANGES)

    log_moderate = ModerateLog(
        user_id=user_id,
        updated_at=datetime.now(UTC_PLUS_5).replace(microsecond=0).replace(tzinfo=None)
    )

    await req.save_profile_data(log_moderate)

    await dialog_manager.done()


window_edit_confirm = Window(
    Format("Завершение изменений"),
    Back(Const("🔙 Назад"), id="back_edit"),
    Button(Const("Подтвердить"), id="edit_confirm", on_click=edit_confirm),
    state=EditDialog.confirm
)


# window_edit_answer = Window(
#     Format("Изменения отправлены на модерацию"),
#     Back(Const("🔙 Назад"), id="back_start"),
#     state=EditDialog.answer,
# )
