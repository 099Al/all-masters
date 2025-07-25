from aiogram import F

from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const

from src.database.connect import DataBase
from src.database.models import UserStatus, Specialist, ModerateStatus
from src.handlers.checkin.profile_state import CheckinDialog, EditDialog
from aiogram.types import CallbackQuery
from sqlalchemy.future import select

from src.log_config import *
logger = logging.getLogger(__name__)



async def back_to_start(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()


async def getter_info(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.start_data

    status = data.get("status")
    moderate_result = data.get("moderate_result")
    message_to_user = data.get("message_to_user")

    data_info = {}
    if status == UserStatus.NEW:
        data_info["info"] = "Ваша заявка ждет модерации."
    elif status == UserStatus.APPROVED and (moderate_result == ModerateStatus.APPROVED or moderate_result is None):
        data_info["info"] = "Ваша анкета открыта."
    elif status == UserStatus.APPROVED and moderate_result in [ModerateStatus.NEW_CHANGES, ModerateStatus.NEW]:
        data_info["info"] = "Внесенные данные ждут модерации."
    elif status == UserStatus.NEW and moderate_result == ModerateStatus.REJECTED:
        reason = f"\nПричина: {message_to_user}" if message_to_user else ''
        data_info["info"] = f"Ваша анкета отклонена. {reason}"
    elif status == UserStatus.APPROVED and moderate_result == ModerateStatus.REJECTED:
        reason = f"\nПричина: {message_to_user}" if message_to_user else ''
        data_info["info"] = f"новые данные отклонены. {reason}"
    elif status == UserStatus.BANNED:
        data_info["info"] = f"Ваша анкета заблокирована."

    available_change = status not in [UserStatus.BANNED]

    data_info["available_change"] = available_change

    return data_info


async def update_info(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    user_data = dialog_manager.start_data
    await dialog_manager.start(EditDialog.name, data=user_data)


window_info = Window(
        Format("{info}"),
                Button(Const("Внести изменения"), id="update_info", on_click=update_info, when=F["available_change"]),
                Button(Const("Назад"), id="back_start", on_click=back_to_start),
                getter=getter_info,
                state=CheckinDialog.info_message,

)