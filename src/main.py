import asyncio
import json

from aiogram_dialog import setup_dialogs
from aiogram import Dispatcher, Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from src.config import settings
from src.config_paramaters import load_from_redis, reload_from_redis, CONFIG_CHANNEL, sync_config_from_db
from src.config_paramaters import configs

from src.database.connect import DataBase

from src.handlers.maintenance_middleware import MaintenanceMiddleware
from src.handlers.menu.menu import set_menu
from src.handlers.routers import add_routers

from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from redis.asyncio import Redis
from enum import Enum

from src.log_config import *
#from src.scheduled.db import init_pool

logger = logging.getLogger(__name__)


bot = Bot(token=settings.TOKEN_ID, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def config_listener(redis):
    pubsub = redis.pubsub()
    await pubsub.subscribe(CONFIG_CHANNEL)
    async for msg in pubsub.listen():
        if msg.get("type") == "message":
            await reload_from_redis(redis)


def dumps_with_enum(obj):
    def default(o):
        if isinstance(o, Enum):
            return o.value  # or o.name
        # Last resort fallback (optional):
        return str(o)
    return json.dumps(obj, default=default)
redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB_FSM)
storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True), json_dumps=dumps_with_enum)



dp = Dispatcher(storage=storage)


# @dp.startup()
# async def on_startup(*_):
#     await init_pool()



async def start():

    db = DataBase()
    await db.create_db()

    await set_menu(bot)


    # 1) при старте: синкнуть БД -> Redis (если хочешь)
    redis_config = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB_CONFIG)
    sm = db.get_session()
    await sync_config_from_db(sm, redis_config)

    # 2) загрузить локально из Redis
    await load_from_redis(redis_config)

    # 3) слушать pubsub и обновлять локально
    asyncio.create_task(config_listener(redis_config))

    #dp["redis"] = redis
    #dp["db_sm"] = sm


    mw = MaintenanceMiddleware(
        enabled=True,  # стартуем в режиме техработ
        admin_ids=configs.ADMIN_IDS,
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