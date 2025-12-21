import os

from aiogram import Bot
from aiogram.types import Message

from aiogram import Router
from aiogram.filters import Command
from aiogram_dialog import DialogManager

from src.config import settings
from src.database.models import UserStatus, SpecialistPhotoType, ModerateStatus
from src.database.requests_db import ReqData
from src.handlers.checkin.profile_state import CheckinDialog, CheckinUserDialog

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
            await dialog_manager.start(CheckinUserDialog.ban_message)
            return

    res = await req.get_specialist_data(user_id)

    if not res:
        return

    # default fallback
    collage_location = res.photo_location
    collage_name = res.photo_name

    def collage_exists(location: str, name: str) -> bool:
        path = f"{settings.path_root}/{location}/{name}"
        return os.path.exists(path)

    if res.status == UserStatus.NEW:
        try:
            photos = await req.get_moderate_photos(user_id, SpecialistPhotoType.COLLAGE)
            if photos:
                location, name = photos[0]
                if collage_exists(location, name):
                    collage_location = location
                    collage_name = name
        except Exception as e:
            logger.error(
                f"Error in start No collage. bot_id: {bot.id}. {e}"
            )

    elif res.status == UserStatus.ACTIVE:
        if res.moderate_result == ModerateStatus.NEW_CHANGES:
            location = settings.NEW_COLLAGE_IMG
            name = f"{user_id}_collage.jpg"

            if collage_exists(location, name):
                collage_location = location
                collage_name = name

        else:
            photos = await req.get_specialist_photos(user_id, SpecialistPhotoType.COLLAGE)
            if photos:
                location, name = photos[0]
                if collage_exists(location, name):
                    collage_location = location
                    collage_name = name


        user_data = {"user_id": user_id,
                 "photo_telegram": res.photo_telegram,
                 "photo_location": res.photo_location,
                 "photo_name": res.photo_name,
                 "collage_location": collage_location,
                 "collage_name": collage_name,
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