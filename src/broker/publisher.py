import asyncio
from datetime import datetime

import nats


async def main():
    # Подключаемся к серверу NATS
    nc = await nats.connect("nats://127.0.0.1:4222")

    # Желаемая задержка в секундах
    delay = 5

    # Сообщение для отправки
    message = 'Hello from Python-publisher!'

    # Заголовки
    headers = {
        'Tg-Delayed-Msg-Timestamp': str(datetime.now().timestamp()),
        'Tg-Delayed-Msg-Delay': str(delay)
    }

    # Сабджект, в который отправляется сообщение
    subject = 'aiogram.delayed.messages'

    # Публикуем сообщение на указанный сабджект
    await nc.publish(subject, message.encode(encoding='utf-8'), headers=headers)

    # Выводим в консоль информацию о том, что сообщение опубликовано
    print(f"Message '{message}' with headers {headers} published in subject `{subject}`")

    # Закрываем соединение
    await nc.close()


asyncio.run(main())