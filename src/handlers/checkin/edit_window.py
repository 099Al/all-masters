from datetime import datetime
import re
from io import BytesIO

from aiogram.types import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Back, Next, Cancel, RequestContact
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory

from PIL import Image

from src.config import settings
from src.config_paramaters import UTC_PLUS_5
from src.database.models import Specialist, UserStatus, ModerateData, ModerateStatus, ModerateLog, \
    ModerateSpecialistPhoto, SpecialistPhotoType
from src.database.requests_db import ReqData
from src.handlers.checkin.profile_state import CheckinDialog, EditDialog


from src.log_config import *
from src.utils.utils import make_collage, digit_hash

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
    await dialog_manager.switch_to(EditDialog.services)


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


async def getter_edit_services(dialog_manager: DialogManager, **kwargs):
    user_data = dialog_manager.start_data
    return {"services": user_data['services']}

async def edit_services(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['services'] = message.text
    await dialog_manager.switch_to(EditDialog.about)

window_edit_services = Window(
    Format("Ваши услуги: {services}\nДля изменения введите новое значение"),
    TextInput(id="edit_services",
              type_factory=str,
              on_success=edit_services,
              ),
    Back(Const("🔙 Назад"), id="back_edit_services"),
    Next(Const("⏩ Пропустить"), id="skip"),
    state=EditDialog.services,
    getter=getter_edit_services
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
    await dialog_manager.switch_to(EditDialog.edit_photo_works)

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





async def getter_edit_photo_works(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data['photo_works'] = {}
    return {}

async def edit_photo_works(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data['photo_works'] = {1: message.photo[-1].file_id}

    await dialog_manager.switch_to(EditDialog.edit_photo_works_another)

async def skip_edit_photo_works(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(EditDialog.message_to_admin)

window_edit_works_photo = Window(
                Format("Добавьте фото ваших работ\n(не более 5)"),
                MessageInput(id="input_edit_photo_works",
                          func=edit_photo_works,
                          content_types=ContentType.PHOTO
                          ),
                Back(Const("🔙 Назад"), id="back_photo"),
                Button(Const("⏩ Пропустить"), id="skip_works_photo", on_click=skip_edit_photo_works),
                state=EditDialog.edit_photo_works,
                getter=getter_edit_photo_works
)


async def edit_another_photo_works(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    d_works_photo = dialog_manager.dialog_data.get('photo_works', {})
    d_len = len(d_works_photo)
    if d_len == 0:
        dialog_manager.dialog_data['photo_works'] = {1: message.photo[-1].file_id}
    else:
        d_works_photo.update({d_len + 1: message.photo[-1].file_id})

    if d_len + 1 >= 5:
        await dialog_manager.switch_to(EditDialog.message_to_admin)

async def skip_edit_photo_works(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(EditDialog.message_to_admin)

async def getter_another_works_photo(dialog_manager: DialogManager, **kwargs):
    d_works_photo = dialog_manager.dialog_data.get('photo_works', {})
    return {
        "photo_works_cnt": 5 - len(d_works_photo)
    }


window_edit_another_works_photo = Window(
                Format("Добавьте еще фото\n(осталось {photo_works_cnt}"),
                MessageInput(id="input_another_photo_works",
                          func=edit_another_photo_works,
                          content_types=ContentType.PHOTO
                          ),
                Back(Const("🔙 Назад"), id="back_another_photo"),
                Button(Const("⏩ Далее"), id="skip_works_photo", on_click=skip_edit_photo_works),
                state=EditDialog.edit_photo_works_another,
                getter=getter_another_works_photo
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
    location_path = None
    name_photo = None

    bot = callback.from_user.bot
    if img_telegram_id:
        location_path = f"{settings.NEW_AVATAR_IMG}"
        name_photo = f"{user_id}.jpg"
        await bot.download(img_telegram_id, destination=f"{settings.path_root}/{location_path}/{name_photo}")
    else:
        local_path = None

    specialist_status = dialog_manager.start_data['status']

    #TODO: update Specialist moderate_result to NEW_CHANGES
    #start_data - это информация из Specialist и MooderateData (информация в ModerateData в приоритете)


    specialist_moderate = ModerateData(
        id=user_id,
        status=ModerateStatus.NEW_CHANGES,
        name=dialog_manager.dialog_data.get('name', dialog_manager.start_data['name']),
        phone=dialog_manager.dialog_data.get('phone', dialog_manager.start_data['phone']),
        telegram=dialog_manager.dialog_data.get('telegram', dialog_manager.start_data['telegram']),
        email=dialog_manager.dialog_data.get('email', dialog_manager.start_data['email']),
        services=dialog_manager.dialog_data.get('services', dialog_manager.start_data['services']),
        about=dialog_manager.dialog_data.get('about', dialog_manager.start_data['about']),
        photo_telegram=img_telegram_id or dialog_manager.start_data['photo_telegram'],
        photo_location=location_path or dialog_manager.start_data['photo_location'],
        photo_name=name_photo or dialog_manager.start_data['photo_name'],
        updated_at=datetime.now(UTC_PLUS_5).replace(microsecond=0).replace(tzinfo=None),
        message_to_admin=dialog_manager.dialog_data.get('message_to_admin')
    )

    req = ReqData()
    await req.merge_profile_data(specialist_moderate)
    await req.update_specialist(user_id, moderate_result=ModerateStatus.NEW_CHANGES)   #TODO: возможно нужно убрать. См. замечание в info_window

    d_works_photo = dialog_manager.dialog_data.get('photo_works', None)
    if d_works_photo:

        old_work_photos = await req.get_moderate_photos(user_id, SpecialistPhotoType.WORKS)

        if old_work_photos:
            await req.delete_moderate_work_photo(user_id, SpecialistPhotoType.WORKS)

        for ph in old_work_photos:
            ph_location = ph.photo_location
            ph_name = ph.photo_name
            ph_path = f"{settings.path_root}/{ph_location}/{ph_name}"
            if os.path.exists(ph_path):
                os.remove(ph_path)


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
            location_work_photo = f"{settings.NEW_WORKS_IMG}"
            name_work_photo = f"{user_id}_{str(k)}_{digit_hash(pid)}.jpg"
            await bot.download(pid, destination=f"{settings.path_root}/{location_work_photo}/{name_work_photo}")


    # else:
    #     old_work_photos = await req.get_moderate_photos(user_id, SpecialistPhotoType.WORKS)
    #     if old_work_photos:
    #         d_works_photo = old_work_photos
    #     else:
    #         d_works_photo = await req.get_specialist_photos(user_id, SpecialistPhotoType.WORKS)


    bot = dialog_manager.middleware_data['bot']
    photo_collage = None


    path_to_collage = f"{settings.path_root}/{settings.NEW_COLLAGE_IMG}/{callback.from_user.id}_collage.jpg"

    if os.path.exists(path_to_collage):
        os.remove(path_to_collage)

    photo_location = location_path or dialog_manager.start_data['photo_location']  #new or old
    photo_name = name_photo or dialog_manager.start_data['photo_name']
    photo_path = f"{settings.path_root}/{photo_location}/{photo_name}"

    pil_images = []
    if os.path.exists(photo_path):
        pil_images.append(Image.open(photo_path).convert("RGB"))  #new or old photo

    if d_works_photo:
        #new photos
        for pid in list(d_works_photo.values()):
            file = await bot.get_file(pid)
            file_bytes = await bot.download_file(file.file_path)
            pil_images.append(Image.open(BytesIO(file_bytes.read())).convert("RGB"))
    else:
        if img_telegram_id:
            moderate_works_photos = await req.get_moderate_photos(user_id, SpecialistPhotoType.WORKS)
            if moderate_works_photos:
                for ph in moderate_works_photos:
                    file_path = f"{settings.path_root}/{ph.photo_location}/{ph.photo_name}"
                    if os.path.exists(file_path):
                        pil_images.append(Image.open(file_path).convert("RGB"))
            else:
                works_photos = await req.get_specialist_photos(user_id, SpecialistPhotoType.WORKS)
                if works_photos:
                    for ph in works_photos:
                        file_path = f"{settings.path_root}/{ph.photo_location}/{ph.photo_name}"
                        if os.path.exists(file_path):
                            pil_images.append(Image.open(file_path).convert("RGB"))


    if pil_images:
        buff_collage = make_collage(pil_images)
        buff_collage.seek(0)

        with open(path_to_collage, "wb") as f:
            f.write(buff_collage.getvalue())

        moderate_collage = ModerateSpecialistPhoto(
            specialist_id=user_id,
            photo_location=f"{settings.NEW_COLLAGE_IMG}",
            photo_name=f"{user_id}_collage.jpg",
            photo_type=SpecialistPhotoType.COLLAGE,
            created_at=datetime.now(UTC_PLUS_5).replace(tzinfo=None),
            photo_telegram_id=None
        )

        await req.save_profile_data(moderate_collage)

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
