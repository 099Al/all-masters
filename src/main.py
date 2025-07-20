import asyncio

from aiogram_dialog import setup_dialogs
from aiogram import Dispatcher, Bot, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from config import settings

import logging

from src.handlers.routers import add_routers

logger = logging.getLogger(__name__)



async def start():

    bot = Bot(token=settings.TOKEN_ID, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    add_routers(dp)



    setup_dialogs(dp)

    await dp.start_polling(bot, skip_updates=True)




if __name__ == '__main__':
    db = settings.DB

    logging.basicConfig(filename='logs/shop.log', level=logging.ERROR)
    asyncio.run(start())