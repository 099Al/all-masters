from aiogram_dialog import Dialog, DialogManager, StartMode, Window

from src.handlers.checkin.edit_window import (window_edit_name,  # window_edit_phone,
                                              window_edit_email, window_edit_services, window_edit_about,
                                              window_edit_photo, window_edit_confirm, window_edit_phone,
                                              window_message_to_admin
                                              )
from src.handlers.checkin.info_window import window_info
from src.handlers.checkin.checkin_windows import (
    window_checkin_start, window_name, window_phone, window_email,
    window_services, window_about, window_photo, window_confirm, window_answer
)

dialog_checkin = Dialog(
window_info,
    window_checkin_start,
    window_phone,
    window_email,
    window_name,
    window_services,
    window_about,
    window_photo,
    window_confirm,
    window_answer
)


dialog_edit = Dialog(
window_edit_name,
    window_edit_phone,
    window_edit_email,
    window_edit_services,
    window_edit_about,
    window_edit_photo,
    window_message_to_admin,
    window_edit_confirm
)
