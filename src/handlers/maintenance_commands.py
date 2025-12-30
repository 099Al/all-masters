# src/handlers/maintenance_commands.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Dispatcher

from src.config_paramaters import configs

import src.log_settings
import logging
logger = logging.getLogger(__name__)

maintenance_cmds_router = Router(name="maintenance_cmds")

@maintenance_cmds_router.message(Command("maintenance_on"))
async def maintenance_on(message: Message, dispatcher: Dispatcher):
    try:
        if message.from_user.id not in configs.ADMIN_IDS:
            return
        dispatcher["maintenance_mw"].turn_on()
        await message.answer("⚙️ Режим обслуживания включён.")
        logger.info(f"maintenance_on. bot_id: {message.bot.id}.")
    except Exception as e:
        logger.error(f"Error in maintenance_on. bot_id: {message.bot.id}. {e}")

@maintenance_cmds_router.message(Command("maintenance_off"))
async def maintenance_off(message: Message, dispatcher: Dispatcher):
    try:
        if message.from_user.id not in configs.ADMIN_IDS:
            return
        dispatcher["maintenance_mw"].turn_off()
        await message.answer("✅ Режим обслуживания выключен.")
        logger.info(f"maintenance_off. bot_id: {message.bot.id}.")
    except Exception as e:
        logger.error(f"Error in maintenance_off. bot_id: {message.bot.id}. {e}")