from aiogram_dialog import Dialog, DialogManager, StartMode, Window

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

