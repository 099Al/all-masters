from aiogram import Dispatcher

from src.handlers.check.test import test_router
from src.handlers.checkin.profile_dialogs import dialog_checkin, dialog_edit, dialog_checkin_user
from src.handlers.menu.profile_handler import menu_router
from src.handlers.menu.start import start_router, dialog_start
from src.handlers.menu.search import dialog_search, search_router

from src.handlers.maintenance_commands import maintenance_cmds_router


def add_routers(dp: Dispatcher):
    dp.include_router(maintenance_cmds_router)
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(search_router)

    dp.include_router(test_router)


    #Диалоги
    dp.include_router(dialog_start)
    dp.include_router(dialog_checkin)
    dp.include_router(dialog_checkin_user)
    dp.include_router(dialog_edit)
    dp.include_router(dialog_search)

