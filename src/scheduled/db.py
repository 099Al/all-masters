import asyncpg

from src.config import settings

_pool: asyncpg.Pool | None = None

async def init_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(settings.pool_url)

async def get_pool() -> asyncpg.Pool:
    if _pool is None:
        await init_pool()
    return _pool
