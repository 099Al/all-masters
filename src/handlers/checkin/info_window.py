from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.enums import ContentType

from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.api.entities import MediaAttachment, MediaId

from sqlalchemy.future import select

from src.config_paramaters import EDIT_REQUEST_LIMIT
from src.database.connect import DataBase
from src.database.models import UserStatus, Specialist, ModerateStatus, UserModerateResult
from src.database.requests_db import ReqData
from src.handlers.checkin.profile_state import CheckinDialog, EditDialog

from src.log_config import *
logger = logging.getLogger(__name__)


async def back_to_start(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()


async def update_data(data):
    req = ReqData()
    res_m = await req.get_moderate_date(data['user_id'])

    # merge Specialist and ModerateData
    if res_m.name:
        data['name'] = res_m.name
    if res_m.phone:
        data['phone'] = res_m.phone
    if res_m.telegram:
        data['telegram'] = res_m.telegram
    if res_m.email:
        data['email'] = res_m.email
    if res_m.specialty:
        data['specialty'] = res_m.specialty
    if res_m.about:
        data['about'] = res_m.about
    if res_m.photo_telegram:
        data['photo_telegram'] = res_m.photo_telegram


async def getter_info(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.start_data

    status = data.get("status")
    moderate_result = data.get("moderate_result")
    message_to_user = data.get("message_to_user")
    photo_telegram = data.get("photo_telegram")

    data_info = {'available_change': True}

    req = ReqData()
    cnt_req = await req.get_cnt_edit_request(data['user_id'])


    if cnt_req >= EDIT_REQUEST_LIMIT:
        await req.update_specialist(data['user_id'], moderate_result=UserModerateResult.DELAY)
        moderate_result = UserModerateResult.DELAY
        data_info["available_change"] = False

    if status == UserStatus.NEW and moderate_result is None:
        data_info["info"] = "Ваша заявка ждет модерации."
    elif status == UserStatus.NEW and moderate_result == UserModerateResult.NEW_CHANGES:
        data_info["info"] = "Ваша заявка ждет модерации."
        await update_data(data)
    elif status == UserStatus.NEW and (moderate_result == UserModerateResult.DELAY):
        data_info["info"] = "Ваша заявка ждет модерации.\nОт вас слишком много запросов.\nПопробуйте внести изменения позже"
        await update_data(data)
        data_info["available_change"] = False
    elif status == UserStatus.NEW and moderate_result == UserModerateResult.REJECTED:
        data_info["info"] = f"Ваша анкета отклонена.\nПричина:{message_to_user}"
    elif status == UserStatus.ACTIVE and moderate_result == UserModerateResult.APPROVED:
        data_info["info"] = f"Ваша анкета одобрена.\nТеперь вы доступны для пользователей."
    elif status == UserStatus.ACTIVE and moderate_result == UserModerateResult.NEW_CHANGES:
        data_info["info"] = f"Новые данные на модерации."
        await update_data(data)
    elif status == UserStatus.ACTIVE and moderate_result == UserModerateResult.DELAY:
        data_info["info"] = f"Ваша анкета на модерации.\nОт вас слишком много запросов.\nПопробуйте внести изменения позже"
        await update_data(data)
        data_info["available_change"] = False
    elif status == UserStatus.ACTIVE and moderate_result == UserModerateResult.REJECTED:
        data_info["info"] = f"Новые изменения отклонены.\nПричина:{message_to_user}"
    elif status == UserStatus.BANNED:
        data_info["info"] = f"Ваша анкета заблокирована.\nПричина:{message_to_user}"
        data_info["available_change"] = False

    if photo_telegram:
        image = MediaAttachment(ContentType.PHOTO, file_id=MediaId(photo_telegram))
        #image = MediaAttachment(ContentType.PHOTO, path=r'full_path\src\images\ .jpg')
        data_info["photo"] = image

    data_info["profile_info"] = f"Имя: {data['name']}\nТелефон: {data['phone']}\nTelegram: {data['telegram']}\nEmail: {data['email']}\nСпециальность: {data['specialty']}\nО себе: {data['about']}"

    return data_info



async def update_info(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    user_data = dialog_manager.start_data
    await dialog_manager.start(EditDialog.name, data=user_data)


window_info = Window(
                DynamicMedia("photo", when=F["photo"]),
                Format("<b>{info}</b>"),
                Format("{profile_info}"),
                Button(Const("Внести изменения"), id="update_info", on_click=update_info, when=F["available_change"]),
                Button(Const("Назад"), id="back_start", on_click=back_to_start),
                getter=getter_info,
                state=CheckinDialog.info_message,

)


