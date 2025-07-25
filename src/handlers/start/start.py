from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Format, Const, List
from sqlalchemy.future import select

from src.database.connect import DataBase
from src.database.models import Specialist, ModerateData, UserStatus
from src.handlers.checkin.checkin_state import CheckinDialog
from src.handlers.start.start_state import StartDialog

#from src.log_config import *

from src.log_settings import *
import logging
logger = logging.getLogger(__name__)


start_router = Router()

@start_router.message(Command(commands='start'))
async def start_menu(message: Message, dialog_manager: DialogManager):
    try:
        #await message.answer("Добро пожаловать в каталог мастеров!")
        await dialog_manager.start(StartDialog.start, mode=StartMode.RESET_STACK)
    except Exception as e:
        logger.error(f"Error in start. bot_id: {message.bot.id}. {e}")


async def user_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """
    Пользователь заходит 1й раз. Предлагается зарегистрироваться
    Данные попадают в Specialist (id, status=NEW, и поля по дефолту: на модерации)

    Пользователь заходит после регистрации:
    Проверяется наличие в Specialist по id и статус.
    Если NEW, значит пользователь валидируется 1й раз.
    Берем данные из ModerateData. При редоктировании показываем их.
    Если статус в Specialict APPROVED, то ищем данные в ModerateData, т.к. могли произойти доп. изменения.
    И пользователя для редактирования показываем данные из ModerateData, но message_to_user из Specialist,
    т.к. на основании него были отправлены данные в ModerateData (пользователь сейчас активный)
    """
    user_id = callback.from_user.id
    session = DataBase().get_session()

    async with session() as session:
        result = await session.execute(
            select(Specialist)
            .where(Specialist.id == user_id)
        )
        res = result.scalars().first()

    if res:
        user_data = {"user_id": user_id,
                 "name": res.name,
                 "phone": res.phone,
                 "email": res.email,
                 "telegram": res.telegram,
                 "specialty": res.specialty,
                 "about": res.about,
                 "status": res.status,
                 "moderate_result": res.moderate_result,
                 "message_to_user": res.message_to_user
                 }
        await dialog_manager.start(CheckinDialog.info_message, data=user_data)
    else:
        await dialog_manager.start(CheckinDialog.offer_message)


async def search_user(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


dialog_start = Dialog(
        Window(
            Format("Выберите действие"),
            Button(Const("Поиск мастеров"), id="search_master", on_click=search_user),
            Button(Const("Я Мастер"), id="i_am_master", on_click=user_registration),
            state=StartDialog.start,
        )
    )



