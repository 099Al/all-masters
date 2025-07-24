from aiogram import F

from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const

from src.database.connect import DataBase
from src.database.models import UserStatus, Specialist
from src.handlers.checkin.checkin_state import CheckinDialog, EditDialog
from aiogram.types import CallbackQuery
from sqlalchemy.future import select

from src.log_config import *
logger = logging.getLogger(__name__)



async def back_to_start(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()


async def getter_info(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.start_data

    status = data.get("status")
    message_to_user = data.get("message_to_user")

    data_info = {}
    if status == UserStatus.NEW:
        data_info["info"] = "Ваша заявка ждет модерации."
    elif status == UserStatus.APPROVED:
        data_info["info"] = "Ваша анкета открыта."
    elif status == UserStatus.NEW_CHANGES:
        data_info["info"] = "Внесенные данные ждут модерации."
    elif status == UserStatus.REJECTED:
        reason = f"\nПричина: {message_to_user}" if message_to_user else ''
        data_info["info"] = f"Ваша анкета отклонена. {reason}"
    elif status == UserStatus.BANNED:
        data_info["info"] = f"Ваша анкета заблокирована."
    elif status == UserStatus.DELETED:
        data_info["info"] = f"Ваша анкета удалена."

    button_change = status not in [UserStatus.BANNED]

    data_info["button_change"] = button_change

    return data_info


async def update_info(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.start_data["user_id"]
    session = DataBase().get_session()
    async with session() as session:
        result = await session.execute(
            select(Specialist)
            .where(Specialist.id == user_id)
        )
    res = result.scalars().first()

    user_data = {"user_id": user_id,
                 "name": res.name,
                 "phone": res.phone,
                 "email": res.email,
                 "specialty": res.specialty,
                 "about": res.about
                 }
    await dialog_manager.start(EditDialog.name, data=user_data)



window_info = Window(
        Format("{info}"),
                Button(Const("Внести изменения"), id="update_info", on_click=update_info, when=F["button_change"]),
                Button(Const("Назад"), id="back_start", on_click=back_to_start),
                getter=getter_info,
                state=CheckinDialog.info_message,

)