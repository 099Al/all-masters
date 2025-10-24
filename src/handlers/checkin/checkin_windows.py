from datetime import datetime
import re
from io import BytesIO
from urllib import request

from aiogram.fsm.context import FSMContext
from aiogram import Dispatcher, Bot
from aiogram.types import ContentType
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Back, Next
from aiogram_dialog.widgets.text import Format, Const, List
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram import Bot, F

from PIL import Image


from src import config
from src.config import settings
from src.config_paramaters import UTC_PLUS_5
from src.database.connect import DataBase
from src.database.models import Specialist, ModerateData, ModerateStatus, UserStatus, SpecialistPhoto, \
    SpecialistPhotoType, ModerateSpecialistPhoto
from src.database.requests_db import ReqData
from src.handlers.checkin.profile_state import CheckinDialog
from aiogram.types import CallbackQuery

from src.log_config import *
from aiogram_dialog.widgets.kbd import RequestContact

from src.utils.utils import make_collage, digit_hash

logger = logging.getLogger(__name__)


async def checkin(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    #await dialog_manager.switch_to(CheckinDialog.request_phone)
    #телефон уже есть в таблице Users
    await dialog_manager.switch_to(CheckinDialog.name)

async def back_to_start(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()



window_checkin_start = Window(
                Format("Зарегистрируйтесь \nи клиенты смогут вас найти!"),
                Button(Const("Зарегистрироваться"), id="checkin", on_click=checkin),
                Button(Const("Назад"), id="back_start", on_click=back_to_start),
                state=CheckinDialog.checkin_message,
)


# async def contact_message(message: Message, widget: MessageInput, dialog_manager: DialogManager):
#     dialog_manager.dialog_data['phone'] = message.contact.phone_number
#     dialog_manager.dialog_data['telegram'] = message.from_user.username
#     await dialog_manager.switch_to(CheckinDialog.email)


# window_phone = Window(
#                 Format("Для регистрации нужен ваш телефон"),
#                 RequestContact(Const("Отправить контакт")),
#                 Back(Const("Назад"), id="back"),
#                 MessageInput(contact_message, ContentType.CONTACT),
#                 markup_factory=ReplyKeyboardFactory(
#                             input_field_placeholder=Format("{event.from_user.username}"),
#                             resize_keyboard=True,
#                             one_time_keyboard=True
#                             ),
#                 state=CheckinDialog.request_phone,
# )

async def save_name(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['name'] = widget.get_value()
    await dialog_manager.switch_to(CheckinDialog.email)

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

window_name = Window(
                Format("Введите ваше имя"),
                TextInput(id="input_name",
                          type_factory=validate_name,
                          on_success=save_name,
                          on_error=error_name
                          ),
                Back(Const("🔙 Назад"), id="back_name"),
                state=CheckinDialog.name
)

async def save_email(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['email'] = message.text
    await dialog_manager.switch_to(CheckinDialog.services)

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

window_email = Window(
                Format("Введите ваш email"),
                TextInput(id="input_email",
                          type_factory=validate_email,
                          on_success=save_email,
                          on_error=error_email
                          ),
                Back(Const("🔙 Назад"), id="back_email"),
                Next(Const("⏩ Пропустить"), id="skip"),
                state=CheckinDialog.email,
)







async def save_service(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['services'] = message.text
    await dialog_manager.switch_to(CheckinDialog.about)

async def error_service(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    await message.answer(error.args[0])

def validate_service(service: str) -> str:
    if len(service) > 100:
        raise ValueError("Слишком большое описание\n Постарайте описать кратко (не более 100 символов)")
    else:
        return service

window_services = Window(
                Format("Опишите кратко услуги, которые вы предоставляете\nНапример: мойка ковров, уборка квартиры"),
                TextInput(id="input_service",
                          type_factory=validate_service,
                          on_success=save_service,
                          on_error=error_service
                          ),
                Back(Const("🔙 Назад"), id="back_service"),
                state=CheckinDialog.services,
)



async def save_about(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['about'] = message.text
    await dialog_manager.switch_to(CheckinDialog.photo)

async def error_about(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    await message.answer(error.args[0])

def validate_about(about: str) -> str:
    if len(about) > 500:
        raise ValueError("Слишком много символов.\n не больше 500")
    else:
        return about

window_about = Window(
                Format("Напишите подробнее о себе.\nМожете указать стоимость работ, адрес\nи другую информацию"),
                TextInput(id="input_about",
                          type_factory=validate_about,
                          on_success=save_about,
                          on_error=error_about
                          ),
                Back(Const("🔙 Назад"), id="back_service"),
                state=CheckinDialog.about,
)



async def save_photo(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data['photo'] = message.photo[-1].file_id
    await dialog_manager.switch_to(CheckinDialog.photo_works)


window_photo = Window(
                Format("Добавьте ваше фото"),
                MessageInput(id="input_photo",
                          func=save_photo,
                          content_types=ContentType.PHOTO
                          ),
                Back(Const("🔙 Назад"), id="back_offer"),
                Next(Const("⏩ Пропустить"), id="skip"),
                state=CheckinDialog.photo,
)

async def getter_photo_works(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data['photo_works'] = {}
    return {}

async def add_photo_works(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data['photo_works'] = {1: message.photo[-1].file_id}

    await dialog_manager.switch_to(CheckinDialog.photo_works_another)

async def skip_photo_works(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(CheckinDialog.confirm)

window_add_works_photo = Window(
                Format("Добавьте фото ваших работ\n(не более 5)"),
                MessageInput(id="input_photo_works",
                          func=add_photo_works,
                          content_types=ContentType.PHOTO
                          ),
                Back(Const("🔙 Назад"), id="back_photo"),
                Button(Const("⏩ Пропустить"), id="skip_works_photo", on_click=skip_photo_works),
                state=CheckinDialog.photo_works,
                getter=getter_photo_works
)


async def add_another_photo_works(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    d_works_photo = dialog_manager.dialog_data.get('photo_works', {})
    d_len = len(d_works_photo)
    if d_len == 0:
        dialog_manager.dialog_data['photo_works'] = {1: message.photo[-1].file_id}
    else:
        d_works_photo.update({d_len + 1: message.photo[-1].file_id})

    if d_len + 1 >= 5:
        await dialog_manager.switch_to(CheckinDialog.confirm)

async def skip_photo_works(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(CheckinDialog.confirm)

async def getter_another_works_photo(dialog_manager: DialogManager, **kwargs):
    d_works_photo = dialog_manager.dialog_data.get('photo_works', {})
    return {
        "photo_works_cnt": 5 - len(d_works_photo)
    }


window_add_another_works_photo = Window(
                Format("Добавьте еще фото\n(осталось {photo_works_cnt}"),
                MessageInput(id="input_another_photo_works",
                          func=add_another_photo_works,
                          content_types=ContentType.PHOTO
                          ),
                Back(Const("🔙 Назад"), id="back_another_photo"),
                Button(Const("⏩ Далее"), id="skip_works_photo", on_click=skip_photo_works),
                state=CheckinDialog.photo_works_another,
                getter=getter_another_works_photo
)


async def getter_confirm(dialog_manager: DialogManager, **kwargs):
    #dialog_manager.dialog_data['telegram'] = kwargs['event_from_user'].username
    user_data = dialog_manager.dialog_data
    req = ReqData()
    user = await req.get_user_data(kwargs['event_from_user'].id)

    dialog_manager.dialog_data['phone'] = user.phone
    dialog_manager.dialog_data['telegram'] = user.telegram

    photo_values = []
    spec_photo = dialog_manager.dialog_data.get('photo', None)
    if spec_photo:
        photo_values = [spec_photo]

    d_works_photo = dialog_manager.dialog_data.get('photo_works', None)

    bot = dialog_manager.middleware_data['bot']
    photo_collage = None

    path_to_collage = f"{settings.path_root}/{settings.NEW_COLLAGE_IMG}/{kwargs['event_from_user'].id}_works.jpg"
    if d_works_photo:
        pil_images = []
        photo_values.extend(list(d_works_photo.values()))
        for pid in photo_values:
            file = await bot.get_file(pid)
            file_bytes = await bot.download_file(file.file_path)
            pil_images.append(Image.open(BytesIO(file_bytes.read())).convert("RGB"))
        buff_collage = make_collage(pil_images)
        buff_collage.seek(0)

        with open(path_to_collage, "wb") as f:
            f.write(buff_collage.getvalue())

        photo_collage = MediaAttachment(ContentType.PHOTO, path=path_to_collage)
        dialog_manager.dialog_data['collage_path'] = path_to_collage

    else:
        file = await bot.get_file(spec_photo)
        file_bytes = await bot.download_file(file.file_path)
        with open(path_to_collage, "wb") as f:
            f.write(file_bytes.getbuffer())

        photo_collage = MediaAttachment(ContentType.PHOTO, path=path_to_collage)



    return {
          "photo_collage": photo_collage
        , "name": user_data.get('name', '-')
        # "phone": user_data['phone']
        , "phone": user.phone
        , "telegram": '@' + kwargs['event_from_user'].username
        , "email": user_data.get('email', '-')
        , "services": user_data.get('services', '-')
        , "about": user_data.get('about', '-')
    }

window_confirm = Window(
    DynamicMedia("photo_collage", when=F["photo_collage"]),
    Format("Осталось подтвердить заявку"),
    Format("Подтверждая заявку, вы даете соглашаетесь с условиями использования сервиса"),
    #TODO Link to Site Politics
    Format("<b>Ваши данные:</b>\n<b>Имя:</b> {name}\n<b>Телефон:</b> {phone}\n<b>Telegram:</b> {telegram}\n<b>Email:</b> {email}\n<b>Услуги:</b> {services}\n{about}"),
    Back(Const("🔙 Назад"), id="back_confirm"),
    Next(Const("Подтвердить"), id="confirm"),
    state=CheckinDialog.confirm,
    getter=getter_confirm
)


async def getter_answer(dialog_manager: DialogManager, bot: Bot, event_from_user: User, **kwargs):
    try:
        user_id = event_from_user.id
        img_telegram_id = dialog_manager.dialog_data.get('photo')
        face_local_path = f"{settings.NEW_AVATAR_IMG}"
        face_local_name = f"{user_id}.jpg"

        if img_telegram_id:
            await bot.download(img_telegram_id, destination=f"{settings.path_root}/{face_local_path}/{face_local_name}")
        else:
            face_local_path = None

        specialist_moderate = ModerateData(
            id=user_id,
            status=ModerateStatus.NEW,
            name=dialog_manager.dialog_data.get('name'),
            phone=dialog_manager.dialog_data.get('phone'),
            email=dialog_manager.dialog_data.get('email'),
            telegram=dialog_manager.dialog_data.get('telegram'),
            services=dialog_manager.dialog_data.get('services'),
            about=dialog_manager.dialog_data.get('about'),
            photo_telegram=img_telegram_id,
            photo_location=face_local_path,
            photo_name=face_local_name,
            updated_at=datetime.now(UTC_PLUS_5).replace(tzinfo=None)
        )

        specialist = Specialist(
            id=user_id,
            status=UserStatus.NEW,
            name=dialog_manager.dialog_data.get('name', 'empty'),
            phone=dialog_manager.dialog_data.get('phone', 'empty'),
            email=dialog_manager.dialog_data.get('email'),
            telegram=dialog_manager.dialog_data.get('telegram', 'empty'),
            services=dialog_manager.dialog_data.get('services', 'empty'),
            about=dialog_manager.dialog_data.get('about', 'empty'),
            photo_telegram=img_telegram_id,
            photo_location=face_local_path,
            photo_name=face_local_name,
            created_at=datetime.now(UTC_PLUS_5).replace(tzinfo=None)
        )

        req = ReqData()

        await req.save_profile_data(specialist)
        await req.save_profile_data(specialist_moderate)


        d_works_photo = dialog_manager.dialog_data.get('photo_works', None)
        if d_works_photo:
            photo_values = list(d_works_photo.values())

            specialist_work_photos = [
                ModerateSpecialistPhoto(
                    specialist_id=user_id,
                    photo_location=f"{settings.NEW_WORKS_IMG}",
                    photo_name=f"{user_id}_{str(k)}_{digit_hash(pid)}.jpg",
                    photo_telegram_id=pid,
                    photo_type=SpecialistPhotoType.WORKS,
                    created_at=datetime.now(UTC_PLUS_5).replace(tzinfo=None)
                )
               for k, pid in enumerate(photo_values)
            ]
            await req.save_profile_data(specialist_work_photos)

            for k, pid in enumerate(photo_values):
                file = await bot.get_file(pid)
                file_bytes = await bot.download_file(file.file_path)
                with open(f"{settings.path_root}/{settings.NEW_WORKS_IMG}/{user_id}_{str(k)}_{digit_hash(pid)}.jpg", "wb") as f:
                    f.write(file_bytes.getbuffer())



        path_to_collage = dialog_manager.dialog_data.get('collage_path')
        if path_to_collage:
            photo_collage = ModerateSpecialistPhoto(
                specialist_id=user_id,
                photo_location=f"{settings.NEW_COLLAGE_IMG}",
                photo_name=f"{user_id}_collage.jpg",
                photo_telegram_id=None,
                photo_type=SpecialistPhotoType.COLLAGE,
                created_at=datetime.now(UTC_PLUS_5).replace(tzinfo=None)
            )
            await req.save_profile_data(photo_collage)



    except Exception as e:
        logger.error(f"Error in getter_answer. bot_id: {event_from_user.bot.id}. {e}")

    return {}


window_answer = Window(
                Format("Ваша заявка принята! \nПосле модерации ваша анкета станет доступной пользователям!"),
                Button(Const("Ok"), id="profile_ok", on_click=back_to_start),
                state=CheckinDialog.answer,
                getter=getter_answer
)
