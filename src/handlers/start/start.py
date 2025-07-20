from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message





start_router = Router()



@start_router.message(Command(commands='start'))
async def start_menu(message: Message):
    await message.answer("Добро пожаловать!",
                         #reply_markup=await kb_start_menu(message.from_user.id)
                         )
