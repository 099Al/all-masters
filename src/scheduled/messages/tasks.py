import datetime as dt
from typing import Sequence

import asyncpg
from aiogram import Bot
from taskiq import TaskiqDepends

from src.config_paramaters import BATCH_MESSAGE_LIMIT
from src.database.requests_db import ReqData
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
    db = ReqData()
    total_sent = 0

    while True:
        # 1) берём очередной батч
        rows = await db.fetch_pending_user_messages(BATCH)
        if not rows:
            break

        # 2) отправляем (без троттлинга)
        delivered_ids: list[int] = []
        for r in rows:
            try:
                await bot.send_message(chat_id=r.specialist_id, text=r.message)
                delivered_ids.append(r.id)
            except Exception:
                # тут можете логировать ошибку и продолжать
                pass

        # 3) помечаем доставленные
        if delivered_ids:
            await db.mark_messages_sent(delivered_ids)
            total_sent += len(delivered_ids)

        # цикл продолжится, пока батчи не закончатся

    return total_sent