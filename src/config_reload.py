# tools/reload_config.py
import asyncio
from redis.asyncio import Redis

from src.config import settings
from src.database.connect import DataBase
from src.config_sync import sync_config_from_db

async def main():
    db = DataBase()
    sm = db.get_session()

    redis_config = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB_CONFIG,
    )

    await sync_config_from_db(sm, redis_config)

    await redis_config.close()
    print("OK: config synced DB -> Redis and published")

if __name__ == "__main__":
    asyncio.run(main())
