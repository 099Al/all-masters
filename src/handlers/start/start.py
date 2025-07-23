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
from src.database.models import Specialist
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


async def master_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    user_id = callback.from_user.id
    session = DataBase().get_session()
    async with session() as session:
        result = await session.execute(
            select(Specialist)
            .where(Specialist.id == user_id)
        )

        res = result.scalars().first()

    if res:
        await dialog_manager.start(CheckinDialog.info_message, data={"status": res.status, "message_to_user": res.message_to_user})
    else:
        await dialog_manager.start(CheckinDialog.offer_message)


async def search_master(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


dialog_start = Dialog(
        Window(
            Format("Выберите действие"),
            Button(Const("Поиск мастеров"), id="search_master", on_click=search_master),
            Button(Const("Я Мастер"), id="i_am_master", on_click=master_registration),
            state=StartDialog.start,
        )
    )



