# src/handlers/maintenance_commands.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Dispatcher

from src.config_paramaters import configs

maintenance_cmds_router = Router(name="maintenance_cmds")

@maintenance_cmds_router.message(Command("maintenance_on"))
async def maintenance_on(message: Message, dispatcher: Dispatcher):
    if message.from_user.id not in configs.ADMIN_IDS:
        return
    dispatcher["maintenance_mw"].turn_on()
    await message.answer("⚙️ Режим обслуживания включён.")

@maintenance_cmds_router.message(Command("maintenance_off"))
async def maintenance_off(message: Message, dispatcher: Dispatcher):
    if message.from_user.id not in configs.ADMIN_IDS:
        return
    dispatcher["maintenance_mw"].turn_off()
    await message.answer("✅ Режим обслуживания выключен.")
