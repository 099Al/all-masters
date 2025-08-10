from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_menu(bot: Bot):
    commands = [
        BotCommand(command='/start', description='start'),
        BotCommand(command='/search', description='Поиск мастера'),
        BotCommand(command='/profile', description='Профиль'),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())