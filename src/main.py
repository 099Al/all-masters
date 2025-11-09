import asyncio
import json

from aiogram_dialog import setup_dialogs
from aiogram import Dispatcher, Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from config import settings
from src.broker.locales.mw_i18n import TranslatorRunnerMiddleware
from src.broker.nats_connect import connect_to_nats
from src.broker.start_consumers import start_delayed_consumer
from src.broker.user import user_router
from src.config_paramaters import ADMIN_IDS

from src.database.connect import DataBase
from src.handlers.maintenance_middleware import MaintenanceMiddleware
from src.handlers.menu.menu import set_menu
from src.handlers.routers import add_routers

from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from redis.asyncio import Redis
from enum import Enum
from fluentogram import TranslatorHub
from src.broker.locales.i18n import create_translator_hub

from src.log_config import *
logger = logging.getLogger(__name__)


def dumps_with_enum(obj):
    def default(o):
        if isinstance(o, Enum):
            return o.value  # or o.name
        # Last resort fallback (optional):
        return str(o)
    return json.dumps(obj, default=default)

async def start():

    bot = Bot(token=settings.TOKEN_ID, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    redis = Redis(host='localhost', port=6379, db=0)
    storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True), json_dumps=dumps_with_enum)



    dp = Dispatcher(storage=storage)

    # Подключаемся к NATS и получаем ссылки на клиент и JetStream-контекст
    nc, js = await connect_to_nats(servers=settings.NATS_SERVERS)

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


    dp.include_router(user_router)
    add_routers(dp)
    setup_dialogs(dp)

    translator_hub: TranslatorHub = create_translator_hub()
    dp.update.middleware(TranslatorRunnerMiddleware())


    try:
        await asyncio.gather(
            dp.start_polling(
                bot,
                js=js,
                delay_del_subject=settings.NATS_DELAYED_CONSUMER_SUBJECT,
                _translator_hub=translator_hub
            ),
            start_delayed_consumer(
                nc=nc,
                js=js,
                bot=bot,
                subject=settings.NATS_DELAYED_CONSUMER_SUBJECT,
                stream=settings.NATS_DELAYED_CONSUMER_STREAM,
                durable_name=settings.NATS_DELAYED_CONSUMER_DURABLE_NAME
            )
        )
    except Exception as e:
        logger.exception(e)
    finally:
        await nc.close()
        logger.info('Connection to NATS closed')

    #await dp.start_polling(bot, skip_updates=True)




if __name__ == '__main__':
    #logging.basicConfig(filename='logs/shop.log', level=logging.INFO)

    db = settings.DB



    asyncio.run(start())