from aiogram_dialog import Dialog, DialogManager, StartMode, Window

from src.handlers.checkin.checkin_user_window import window_user_checkin_start, window_user_checkin_ban, \
    window_user_checkin_rules, window_user_checkin_phone, window_user_checkin_done
from src.handlers.checkin.edit_window import (window_edit_name,  # window_edit_phone,
                                              window_edit_email, window_edit_services, window_edit_about,
                                              window_edit_photo, window_edit_confirm, window_edit_phone,
                                              window_message_to_admin, window_edit_works_photo,
                                              window_edit_another_works_photo
                                              )
from src.handlers.checkin.info_window import window_info
from src.handlers.checkin.checkin_windows import (
    window_checkin_start, window_name, window_email,
    window_services, window_about, window_photo, window_confirm, window_answer, window_add_works_photo,
    window_add_another_works_photo
)

dialog_checkin_user = Dialog(
window_user_checkin_ban,
    window_user_checkin_start,
window_user_checkin_rules,
window_user_checkin_phone,
window_user_checkin_done
)


dialog_checkin = Dialog(
window_info,
    window_checkin_start,
    #window_phone,
    window_name,
    window_email,
    window_services,
    window_about,
    window_photo,
    window_add_works_photo,
    window_add_another_works_photo,
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
    window_edit_works_photo,
    window_edit_another_works_photo,
    window_message_to_admin,
    window_edit_confirm
)
