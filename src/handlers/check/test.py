import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

import src.log_settings
import logging

from src.database.requests_db import ReqData

logger = logging.getLogger(__name__)


test_router = Router()


@test_router.message(Command(commands='admin_test'))
async def admin_test(message: Message):
    try:

        user_id = message.from_user.id
        #req = ReqData()
        #res = await req.get_user_data(user_id)

        info = f"user_id:{user_id}"
        # logger.info(f"Test command. Info {info}")
        logger.error(f"Test command. Info {info}")
    except Exception as e:
        logger.error(f"Test command. Error {e}")

@test_router.message(Command(commands='admin_test_db'))
async def admin_test_db(message: Message):
    try:

        await message.answer("test_db")

        user_id = message.from_user.id

        req = ReqData()
        res_1 = await req.get_db_version()
        logger.error(f"INFO Test command. VERSION {res_1}")
        res = await req.get_user_data(user_id)
        logger.error(f"INFO Test command. USER {res}")

        info = f"user_id:{user_id}"
        logger.error(f"INFO Test command. Info {info}")

        await message.answer("test_db___")
    except Exception as e:
        logger.error(f"ERROR Test command. Error {e}")