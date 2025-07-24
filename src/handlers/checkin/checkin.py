from aiogram_dialog import Dialog, DialogManager, StartMode, Window

from src.handlers.checkin.edit_window import (window_edit_name, window_edit_phone,
    window_edit_email, window_edit_specialty, window_edit_about,
    window_edit_photo, window_edit_confirm
                                              )
from src.handlers.checkin.info_window import window_info
from src.handlers.checkin.offer_windows import (
    window_offer_info, window_name, window_phone, window_email,
    window_specialty, window_about, window_photo, window_confirm, window_answer
)

dialog_offer = Dialog(
window_info,
    window_offer_info,
    window_name,
    window_phone,
    window_email,
    window_specialty,
    window_about,
    window_photo,
    window_confirm,
    window_answer
)


dialog_edit = Dialog(
    window_edit_name,
    window_edit_phone,
    window_edit_email,
    window_edit_specialty,
    window_edit_about,
    window_edit_photo,
    window_edit_confirm
)
