from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Format, Const, List


from src.handlers.registration.registarateion_state import RegistrationDialog
from src.handlers.start.start_state import StartDialog

from src.log_config import *
logger = logging.getLogger(__name__)


start_router = Router()

@start_router.message(Command(commands='start'))
async def start_menu(message: Message, dialog_manager: DialogManager):
    try:
        #await message.answer("Добро пожаловать в каталог мастеров!")
        await dialog_manager.start(StartDialog.start, mode=StartMode.RESET_STACK)
        logger.error(f"====Start: {datetime.now().replace(microsecond=0)}. message ==== ")

    except Exception as e:
        logger.error(f"Error in start: {datetime.now().replace(microsecond=0)}. bot_id: {message.bot.id}. {e}")


async def master_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(RegistrationDialog.offer_message)


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



