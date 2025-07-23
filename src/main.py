import asyncio
import sys

from aiogram_dialog import setup_dialogs
from aiogram import Dispatcher, Bot, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from config import settings


from src.database.connect import DataBase
from src.handlers.routers import add_routers

from src.log_config import *
logger = logging.getLogger(__name__)




async def start():

    bot = Bot(token=settings.TOKEN_ID, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    db = DataBase()
    await db.create_db()


    add_routers(dp)



    setup_dialogs(dp)

    await dp.start_polling(bot, skip_updates=True)




if __name__ == '__main__':
    #logging.basicConfig(filename='logs/shop.log', level=logging.INFO)

    db = settings.DB



    asyncio.run(start())