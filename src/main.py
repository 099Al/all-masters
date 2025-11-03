import asyncio

from aiogram_dialog import setup_dialogs
from aiogram import Dispatcher, Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from config import settings
from src.config_paramaters import ADMIN_IDS

from src.database.connect import DataBase
from src.handlers.maintenance_middleware import MaintenanceMiddleware
from src.handlers.menu.menu import set_menu
from src.handlers.routers import add_routers

from src.log_config import *
logger = logging.getLogger(__name__)




async def start():

    bot = Bot(token=settings.TOKEN_ID, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    db = DataBase()
    await db.create_db()


    await set_menu(bot)


    mw = MaintenanceMiddleware(
        enabled=True,  # стартуем в режиме техработ
        admin_ids=ADMIN_IDS,
        allowed_commands={"/help"},  # /help доступен всем
        reply_text="⚙️ Сервис временно недоступен. Идут технические работы."
    )
    dp.message.outer_middleware(mw)
    dp.callback_query.outer_middleware(mw)
    dp["maintenance_mw"] = mw


    add_routers(dp)
    setup_dialogs(dp)

    await dp.start_polling(bot, skip_updates=True)




if __name__ == '__main__':
    #logging.basicConfig(filename='logs/shop.log', level=logging.INFO)

    db = settings.DB



    asyncio.run(start())