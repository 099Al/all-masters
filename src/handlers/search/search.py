from aiogram.types import ContentType
from aiogram.types import CallbackQuery, Message, WebAppInfo
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Back, Next, Cancel, RequestContact, Select, Group, Url, WebApp, ListGroup
from aiogram_dialog.widgets.text import Format, Const, List
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory

from src.database.requests_db import ReqData
from src.handlers.menu.start.start_state import StartDialog
from src.handlers.search.search_state import SearchSpecialistDialog

async def getter_categories(dialog_manager: DialogManager, **kwargs):
    req = ReqData()
    res = await req.get_categories(is_new=False)
    return {'categories': res}

async def select_category(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item_id: int):
    dialog_manager.dialog_data['category'] = item_id
    await dialog_manager.switch_to(SearchSpecialistDialog.service)

async def back_to_start(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await dialog_manager.start(StartDialog.start, mode=StartMode.RESET_STACK)

async def serch_by_user_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    req = ReqData()
    l_spec = await req.find_specialists_by_similarity(text)
    #TODO: перевести в состояние
    print(l_spec)
    return {'specialists': l_spec}



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
    Button(Const("Назад"), id="back_to_start", on_click=back_to_start),
    TextInput(
        id="search",
        type_factory=str,
        on_success=serch_by_user_input
    ),
    state=SearchSpecialistDialog.category,
    getter=getter_categories

)

async def getter_services(dialog_manager: DialogManager, **kwargs):
    category_id = dialog_manager.dialog_data.get('category')

    req = ReqData()
    res = await req.get_services_by_category(category_id=int(category_id), is_new=False)

    return {'services': res}

async def select_service(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item_id: int):
    dialog_manager.dialog_data['service'] = item_id
    # TODO: вывод списка специалистов в WEB
    print('select_service')
    await dialog_manager.switch_to(SearchSpecialistDialog.specialists)


window_services = Window(
    Format("Выберите услугу"),
    Group(
    ListGroup(
        Url(text=Format('{item.name}'),
            url=Const('http://127.0.0.1:8001/profiles/'),
            ),
            WebApp(text=Format('{item.name}'),
            url=Const('https://127.0.0.1:8001/profiles/'),
            ),
            id='service',
            item_id_getter=lambda x: x.id,
            items='services',
    ),
        width = 2
    ),
    Back(Const("Назад"), id="back_to_category_search"),
    TextInput(
        id="search",
        type_factory=str,
        on_success=serch_by_user_input
    ),
    state=SearchSpecialistDialog.service,
    getter=getter_services
)


async def getter_specialists(dialog_manager: DialogManager, **kwargs):
    service_id = dialog_manager.dialog_data.get('service')

    req = ReqData()
    res = await req.get_specialists_by_service(service_id=int(service_id))

    web_app = WebAppInfo(url="http://127.0.0.1:8001/profiles/")

    print('getter_specialists', res)
    return {'specialists': res}

async def select_specialist(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item_id: int):
    print('select_specialist')
    print(item_id)

window_specialists = Window(
    Format("Выберите специалиста"),
    Group(
        Select(
            Format('{item.name}'),
            id='specialist',
            item_id_getter=lambda x: x.id,
            items='specialists',
            on_click=select_specialist
        ),
        width=2
    ),
    Back(Const("Назад"), id="back_to_service_search"),
    state=SearchSpecialistDialog.specialists,
    getter=getter_specialists
)




dialog_search = Dialog(
    window_categories,
    window_services,
    window_specialists
)



