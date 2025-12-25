import json
from sqlalchemy import select

from src.config_paramaters import save_to_redis, publish_updated
from src.database.models import Config


def _parse(v: str):
    try:
        return json.loads(v)
    except Exception:
        return v

async def sync_config_from_db(async_sessionmaker, redis) -> dict:
    """
    1) читает key/value из БД
    2) кладёт в Redis одним JSONом
    3) pubsub notify
    """
    async with async_sessionmaker() as session:
        result = await session.execute(select(Config.key, Config.value))
        rows = result.all()

    data = {k: _parse(v) for k, v in rows}
    await save_to_redis(redis, data)
    await publish_updated(redis)
    return data
