import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

import src.log_settings
import logging
logger = logging.getLogger(__name__)


test_router = Router()


@test_router.message(Command(commands='admin_test'))
async def admin_test(message: Message):
    try:
        #await message.answer("Добро пожаловать в каталог мастеров!")

        user_id = message.from_user.id
        #req = ReqData()
        #res = await req.get_user_data(user_id)

        info = f"user_id:{user_id}"
        # logger.info(f"Test command. Info {info}")
        logger.error(f"Test command. Info {info}")
    except Exception as e:
        logger.error(f"Test command. Error {e}")