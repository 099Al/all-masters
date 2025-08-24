from aiogram.types import ContentType
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Back, Next, Cancel, RequestContact, Select, Group
from aiogram_dialog.widgets.text import Format, Const, List
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory

from src.database.requests_db import ReqData
from src.handlers.search.search_state import SearchSpecialistDialog

async def getter_categories(dialog_manager: DialogManager, **kwargs):
    req = ReqData()
    res = await req.get_categories()
    print('res', res)
    return {'categories': res}

async def select_category(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item_id: str):
    print(item_id)

window_categories = Window(
    Format("Выберите категорию"),
    Group(
        Select(
            Format('{item.name}'),
            id='categ',
            item_id_getter=lambda x: x.id,
            items='categories',
            on_click=select_category
        ),
        width=2
    ),
    state=SearchSpecialistDialog.category,
    getter=getter_categories

)

dialog_search = Dialog(
    window_categories
)



