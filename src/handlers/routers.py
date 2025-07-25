from aiogram import Dispatcher

from src.handlers.checkin.profile import dialog_offer, dialog_edit
from src.handlers.start.start import start_router, dialog_start


def add_routers(dp: Dispatcher):
    dp.include_router(start_router)



    #Диалоги
    dp.include_router(dialog_start)
    dp.include_router(dialog_offer)
    dp.include_router(dialog_edit)