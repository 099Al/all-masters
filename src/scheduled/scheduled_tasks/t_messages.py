import asyncio
import time
from collections import defaultdict

from aiogram import Bot
from taskiq import TaskiqDepends

from src.config_paramaters import BATCH_MESSAGE_LIMIT, SCHEDULE_MESSAGES_TO_USERS
from src.database.requests_db import ReqData
#from src.scheduled.db import get_pool
from src.scheduled.tkq import broker
from aiogram.exceptions import TelegramRetryAfter

# ---- Настройки троттлинга ----
GLOBAL_RPS = 25               # глобальный лимит сообщений/сек на процесс
PER_CHAT_MIN_INTERVAL = 1.2   # минимум 1 сообщение в чат каждые 1.2 c
MAX_CONCURRENCY = 10          # сколько сообщений отправляем параллельно
RETRY_AFTER_PAD = 1.0         # запас к FloodWait в сек

from aiolimiter import AsyncLimiter
_global_limiter = AsyncLimiter(GLOBAL_RPS, time_period=1)

_chat_locks: dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
_last_sent_at: dict[int, float] = defaultdict(lambda: 0.0)

async def _respect_per_chat(chat_id: int) -> None:
    """Гарантирует минимальный интервал между сообщениями в один чат."""
    lock = _chat_locks[chat_id]
    async with lock:
        now = time.monotonic()
        wait = PER_CHAT_MIN_INTERVAL - (now - _last_sent_at[chat_id])
        if wait > 0:
            await asyncio.sleep(wait)
        _last_sent_at[chat_id] = time.monotonic()

async def send_with_throttling(bot: Bot, chat_id: int, text: str) -> bool:
    """Отправка с глобальным RPS, интервалом на чат и обработкой FloodWait (один ретрай)."""
    async with _global_limiter:
        await _respect_per_chat(chat_id)
        try:
            await bot.send_message(chat_id=chat_id, text=text)
            return True
        except TelegramRetryAfter as e:
            # Telegram просит подождать e.retry_after секунд
            await asyncio.sleep(float(e.retry_after) + RETRY_AFTER_PAD)
            async with _global_limiter:
                await _respect_per_chat(chat_id)
                await bot.send_message(chat_id=chat_id, text=text)
            return True
        except Exception:
            # тут можно логировать конкретную ошибку
            return False



# ЕЖЕЧАСНЫЙ CRON. cron_offset — локальная зона (Азия/Алматы).
@broker.task(
    task_name="mailing_user_messages",
    schedule=[SCHEDULE_MESSAGES_TO_USERS],
)
async def mailing_pending(bot: Bot = TaskiqDepends()) -> int:
    """
    Берём все сообщения, где scheduled_at <= now() и sent_at IS NULL,
    отправляем и помечаем как доставленные. Возвращаем кол-во отправок.
    """
    #pool = await get_pool()

    print("==================broadcast_pending_user_messages")

    BATCH = BATCH_MESSAGE_LIMIT
    db = ReqData()
    total_sent = 0

    while True:
        # 1) берём очередной батч
        rows = await db.fetch_pending_user_messages(BATCH)
        if not rows:
            break

        delivered_ids: list[int] = []

        # 2) отправляем (без троттлинга)
        # for r in rows:
        #     try:
        #         await bot.send_message(chat_id=r.specialist_id, text=r.message)
        #         delivered_ids.append(r.id)
        #     except Exception:
        #         # тут можете логировать ошибку и продолжать
        #         pass

        sem = asyncio.Semaphore(MAX_CONCURRENCY)
        async def _one(r):
            async with sem:
                message_to_specialist = f"Вам сообщение от @{r.telegram}:\n\n{r.message}"
                ok = await send_with_throttling(bot, r.specialist_id, message_to_specialist)
                if ok:
                    delivered_ids.append(r.id)

        await asyncio.gather(*[_one(r) for r in rows])

        # 3) помечаем доставленные
        if delivered_ids:
            await db.mark_messages_sent(delivered_ids)
            total_sent += len(delivered_ids)

        # цикл продолжится, пока батчи не закончатся

    return total_sent

