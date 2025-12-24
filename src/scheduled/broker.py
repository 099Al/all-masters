from taskiq_redis import ListQueueBroker
from src.config import settings


url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB_TASKS}"

broker = ListQueueBroker(url=url, queue_name="taskiq:queue")
