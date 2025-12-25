import ast
import json
import asyncio
from dataclasses import dataclass, field
from datetime import timezone, timedelta
from typing import Any

CONFIG_KEY = "app:config:json"
CONFIG_CHANNEL = "app:config:updated"

@dataclass
class Configs:
    UTC_PLUS_5: timezone = timezone(timedelta(hours=5))
    EDIT_REQUEST_LIMIT: int = 4
    SIMILARITY_THRESHOLD: float = 0.4
    ADMIN_IDS: set[int] = field(default_factory=set)
    BATCH_MESSAGE_LIMIT: int = 1000

configs = Configs()
_lock = asyncio.Lock()

def _apply_dict(data: dict[str, Any]) -> None:
    # Приведение типов
    if "UTC_PLUS_5" in data:
        configs.UTC_PLUS_5 = timezone(timedelta(hours=int(data["UTC_PLUS_5"]["utc_shift"])))

    if "EDIT_REQUEST_LIMIT" in data:
        configs.EDIT_REQUEST_LIMIT = int(data["EDIT_REQUEST_LIMIT"])

    if "SIMILARITY_THRESHOLD" in data:
        configs.SIMILARITY_THRESHOLD = float(data["SIMILARITY_THRESHOLD"])

    if "ADMIN_IDS" in data:
        v = data["ADMIN_IDS"]
        configs.ADMIN_IDS = ast.literal_eval(v)

    if "BATCH_MESSAGE_LIMIT" in data:
        configs.BATCH_MESSAGE_LIMIT = int(data["BATCH_MESSAGE_LIMIT"])


async def load_from_redis(redis) -> None:
    """
    Читает конфиг из Redis и применяет в локальный settings.
    """
    raw = await redis.get(CONFIG_KEY)
    if not raw:
        return
    data = json.loads(raw)
    async with _lock:
        _apply_dict(data)


async def save_to_redis(redis, data: dict[str, Any]) -> None:
    """
    Сохраняет конфиг (dict) в Redis (одной json-строкой).
    """
    await redis.set(CONFIG_KEY, json.dumps(data, ensure_ascii=False))


async def publish_updated(redis) -> None:
    """
    Сообщает всем процессам "конфиг обновлён".
    """
    await redis.publish(CONFIG_CHANNEL, "1")


async def reload_from_redis(redis) -> None:
    """
    Принудительно перечитать Redis -> локальный settings.
    """
    await load_from_redis(redis)
