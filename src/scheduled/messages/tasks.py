import datetime as dt
from typing import Sequence

import asyncpg
from aiogram import Bot
from taskiq import TaskiqDepends

from src.config_paramaters import BATCH_MESSAGE_LIMIT
from src.scheduled.messages.db import get_pool
from src.scheduled.messages.tkq import broker


# ЕЖЕЧАСНЫЙ CRON. cron_offset — локальная зона (Азия/Алматы).
@broker.task(
    task_name="broadcast_pending_user_messages",
    schedule=[{"cron": "* * * * *", "cron_offset": "Asia/Almaty"}],
)
async def broadcast_pending(bot: Bot = TaskiqDepends()) -> int:
    """
    Берём все сообщения, где scheduled_at <= now() и sent_at IS NULL,
    отправляем и помечаем как доставленные. Возвращаем кол-во отправок.
    """
    pool = await get_pool()

    BATCH = BATCH_MESSAGE_LIMIT
    sent = 0

    async with pool.acquire() as conn:
        while True:
            rows = await conn.fetch("""
                SELECT id, specialist_id, message
                FROM user_messages
                WHERE sent_at IS NULL
                ORDER BY id
                LIMIT $1
            """, BATCH)

            if not rows:
                break

            delivered_ids = []
            for r in rows:
                try:
                    await bot.send_message(r["specialist_id"], r["message"])
                    delivered_ids.append(r["id"])
                except Exception:
                    pass

            if delivered_ids:
                await conn.execute("""
                    UPDATE user_messages
                    SET sent_at = now()
                    WHERE id = ANY($1::bigint[])
                """, delivered_ids)

            sent += len(delivered_ids)

        return sent
