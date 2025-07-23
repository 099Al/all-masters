from datetime import datetime
from urllib import request

from aiogram.fsm.context import FSMContext
from aiogram import Dispatcher, Bot
from aiogram.types import ContentType
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Back, Next
from aiogram_dialog.widgets.text import Format, Const, List
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput

from src.config import settings
from src.database.connect import DataBase
from src.database.models import Specialist
from src.handlers.registration.registarateion_state import RegistrationDialog
from aiogram.types import CallbackQuery

from src.log_config import *
logger = logging.getLogger(__name__)

IMAGES = 'src/images'


async def registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(RegistrationDialog.name)


async def back_to_start(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()



window_offer_info = Window(
                Format("Зарегистрируйтесь \nи клиенты смогут вас найти!"),
                Button(Const("Зарегистрироваться"), id="registration", on_click=registration),
                Button(Const("Назад"), id="back_start", on_click=back_to_start),
                state=RegistrationDialog.offer_message,
)



async def save_name(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['name'] = widget.get_value()
    print(dialog_manager)
    #await dialog_manager.switch_to(RegistrationDialog.phone)
    await dialog_manager.switch_to(RegistrationDialog.photo)


window_name = Window(
                Format("Введите ваше имя"),
                TextInput(id="input_name",
                          type_factory=str,
                          on_success=save_name
                          ),
                Back(Const("🔙 Назад"), id="back_offer"),
                state=RegistrationDialog.name
)


async def save_phone(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['phone'] = message.text
    await dialog_manager.switch_to(RegistrationDialog.email)

window_phone = Window(
                Format("Введите ваш номер телефона"),
                TextInput(id="input_phone",
                          type_factory=str,
                          on_success=save_phone
                          ),
                Back(Const("🔙 Назад"), id="back_offer"),
                state=RegistrationDialog.phone,
)


async def save_email(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['email'] = message.text
    await dialog_manager.switch_to(RegistrationDialog.specialty)

window_email = Window(
                Format("Введите ваш email"),
                TextInput(id="input_email",
                          type_factory=str,
                          on_success=save_email
                          ),
                Back(Const("🔙 Назад"), id="back_offer"),
                Next(Const("⏩ Пропустить"), id="skip"),
                state=RegistrationDialog.email,
)



async def save_specialty(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['specialty'] = message.text
    await dialog_manager.switch_to(RegistrationDialog.about)

window_specialty = Window(
                Format("Введите вашу специальность"),
                TextInput(id="input_specialty",
                          type_factory=str,
                          on_success=save_specialty
                          ),
                Back(Const("🔙 Назад"), id="back_offer"),
                state=RegistrationDialog.specialty,
)



async def save_about(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['about'] = message.text
    await dialog_manager.switch_to(RegistrationDialog.photo)

window_about = Window(
                Format("Напишите о себе"),
                TextInput(id="input_about",
                          type_factory=str,
                          on_success=save_about
                          ),
                Back(Const("🔙 Назад"), id="back_offer"),
                state=RegistrationDialog.about,
)


async def save_photo(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data['photo'] = message.photo[-1].file_id
    await dialog_manager.switch_to(RegistrationDialog.confirm)


window_photo = Window(
                Format("Добавьте фото"),
                MessageInput(id="input_photo",
                          func=save_photo,
                          content_types=ContentType.PHOTO
                          ),
                Back(Const("🔙 Назад"), id="back_offer"),
                Next(Const("⏩ Пропустить"), id="skip"),
                state=RegistrationDialog.photo,
)


window_confirm = Window(
    Format("Осталось подтвердить заявку"),
    Format("Подтверждая заявку, вы даете соглашаетесь с условиями использования сервиса"),
    #TODO Link to terms
    Back(Const("🔙 Назад"), id="back_offer"),
    Next(Const("Подтвердить"), id="confirm"),
    state=RegistrationDialog.confirm
)


async def getter_answer(dialog_manager: DialogManager, bot: Bot, event_from_user: User, **kwargs):
    try:
        user_id = event_from_user.id
        img_telegram_id = dialog_manager.dialog_data.get('photo')
        local_path = f"{IMAGES}/{user_id}.jpg"

        if img_telegram_id:
            await bot.download(img_telegram_id, destination=f"{settings.path_root}/{local_path}")
        else:
            local_path = None

        specialist = Specialist(
            name=dialog_manager.dialog_data.get('name', 'empty'),
            phone=dialog_manager.dialog_data.get('phone', 'empty'),
            email=dialog_manager.dialog_data.get('email'),
            specialty=dialog_manager.dialog_data.get('specialty', 'empty'),
            about=dialog_manager.dialog_data.get('about', 'empty'),
            photo_telegram=img_telegram_id,
            photo_local=local_path,
            created_at=datetime.now()
        )

        db = DataBase()

        async with db.get_session()() as session:
            async with session.begin():
                session.add(specialist)
    except Exception as e:
        logger.error(f"Error in getter_answer. bot_id: {event_from_user.bot.id}. {e}")

    return {}


window_answer = Window(
                Format("Ваша заявка принята! \nПосле модерации ваша анкета станет доступной в каталоге!"),
                Button(Const("Ok"), id="offer_ok", on_click=back_to_start),
                state=RegistrationDialog.answer,
                getter=getter_answer
)
