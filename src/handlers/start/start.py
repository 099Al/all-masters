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
from src.database.requests_db import ReqData
from src.handlers.checkin.profile_state import CheckinDialog
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
    user_id = callback.from_user.id

    req = ReqData()
    res = await req.get_specialist_date(user_id)

    if res:
        user_data = {"user_id": user_id,
                 "photo_telegram": res.photo_telegram,
                 "photo_local": res.photo_local,
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
        await dialog_manager.start(CheckinDialog.checkin_message)


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



