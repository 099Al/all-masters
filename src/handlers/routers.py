from aiogram import Dispatcher

from src.handlers.checkin.profile import dialog_checkin, dialog_edit, dialog_checkin_user
from src.handlers.menu.commands import menu_router
from src.handlers.menu.start.start import start_router, dialog_start
from src.handlers.search.search import dialog_search

from src.handlers.maintenance_commands import maintenance_cmds_router


def add_routers(dp: Dispatcher):
    dp.include_router(maintenance_cmds_router)
    dp.include_router(start_router)
    dp.include_router(menu_router)



    #Диалоги
    dp.include_router(dialog_start)
    dp.include_router(dialog_checkin)
    dp.include_router(dialog_checkin_user)
    dp.include_router(dialog_edit)
    dp.include_router(dialog_search)
