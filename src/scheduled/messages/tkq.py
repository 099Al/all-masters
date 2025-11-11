import os
from taskiq_redis import ListQueueBroker
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
import taskiq_aiogram

from src.config import settings

broker = ListQueueBroker(url=settings.REDIS_URL)


taskiq_aiogram.init(
    broker,
    "src.main:dp",   # Dispatcher path
    "src.main:bot",  # Bot path
)


scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
