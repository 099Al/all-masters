from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button


from src.database.requests_db import ReqData
from src.handlers.checkin.profile_state import CheckinDialog, CheckinUserDialog
from src.handlers.menu.start.start_state import StartDialog

import logging
logger = logging.getLogger(__name__)



menu_router = Router()


@menu_router.message(Command(commands='profile'))
async def user_registration(message: Message, bot: Bot, dialog_manager: DialogManager):
    user_id = message.chat.id

    req = ReqData()

    res = await req.get_user_data(user_id)
    if res:
        if res.is_banned:
            print(1)
            await dialog_manager.start(CheckinUserDialog.ban_message)
            return



    res = await req.get_specialist_data(user_id)

    if res:
        user_data = {"user_id": user_id,
                 "photo_telegram": res.photo_telegram,
                 "photo_location": res.photo_location,
                 "name": res.name,
                 "phone": res.phone,
                 "email": res.email,
                 "telegram": res.telegram,
                 "services": res.services,
                 "about": res.about,
                 "status": res.status,
                 "moderate_result": res.moderate_result,
                 "message_to_user": res.message_to_user
                 }
        await dialog_manager.start(CheckinDialog.info_message, data=user_data)
    else:
        await dialog_manager.start(CheckinDialog.checkin_message)