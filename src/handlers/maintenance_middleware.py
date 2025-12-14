# src/handlers/maintenance_middleware.py
from typing import Set
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update

class MaintenanceMiddleware(BaseMiddleware):
    def __init__(
        self,
        enabled: bool = True,
        admin_ids: Set[int] | None = None,
        allowed_commands: Set[str] | None = None,  # команды, которые можно всем даже во время техработ
        reply_text: str = "⚙️ Сервис временно недоступен. Идут технические работы."
    ):
        self.enabled = enabled
        self.admin_ids = admin_ids or set()
        self.allowed_commands = allowed_commands or set()
        self.reply_text = reply_text

    # методы для управления из хендлеров
    def turn_on(self):
        self.enabled = True
    def turn_off(self):
        self.enabled = False

    async def __call__(self, handler, event: Update, data: dict):
        # Если техработы выключены — пропускаем
        if not self.enabled:
            return await handler(event, data)

        # Пропускаем неинтересные типы апдейтов
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)

        # Выясняем user_id и "первое слово" для команд
        user_id = None
        first_token = ""

        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            first_token = (event.text or "")
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
            # Кнопкам обычно тоже ставим заглушку
            first_token = ""

        # Админам — полный проход
        if user_id in self.admin_ids:
            return await handler(event, data)

        # Разрешённые команды — пропускаем
        if first_token in self.allowed_commands:
            return await handler(event, data)

        # Всё остальное — заглушка
        if isinstance(event, Message):
            await event.answer(self.reply_text)
        elif isinstance(event, CallbackQuery):
            # можно ответить всплывающим уведомлением
            await event.answer(self.reply_text, show_alert=True)
        return  # НЕ зовём следующий handler
