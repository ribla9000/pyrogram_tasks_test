import datetime
from core.config import BACK_BUTTON_TEXT, SKIP_BUTTON_TEXT, ARROW_LEFT, ARROW_RIGHT
from pyrogram import filters, Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram_patch.router import Router
from pyrogram_patch.fsm.states import State
from pyrogram_patch.fsm.filter import StateFilter
from repository.database.users import UsersRepository
from repository.database.user_tasks import UserTasksRepository
from repository.tools import keyboard_cols
from states.user_tasks import UserTasks
from typing import Union


router = Router()


@router.on_callback_query(filters.regex("task_menu"))
async def task_menu(client: Union[Client, None] = None,
                    callback: Union[CallbackQuery, None] = None,
                    message: Union[Message, None] = None,
                    state: Union[State, None] = None) -> Union[None, Message]:
    await state.finish()
    reply = "There is a task menu"
    back_button = InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="start")
    create_task_button = InlineKeyboardButton(text="Создать задача", callback_data="create_task")
    show_all_tasks_button = InlineKeyboardButton(text="Смотреть все задачи", callback_data="tasks_list,1")
    show_by_filter = InlineKeyboardButton(text="Смотреть по фильтру", callback_data="tasks_filtered,1")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [create_task_button],
            [show_all_tasks_button],
            # [show_by_filter],
            [back_button]
        ]
    )

    if message is not None:
        return await message.reply(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    elif callback is not None:
        return await callback.message.edit_text(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.on_callback_query(filters.regex("create_task"))
async def create_task(client: Client, callback: CallbackQuery, state: State) -> None:
    reply = "Please name this task. This name will be displayed in menu as a button"

    back_button = InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="task_menu")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    await callback.message.edit_text(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    await state.set_state(UserTasks.title)


@router.on_message(StateFilter(UserTasks.title))
async def get_title(client: Client, message: Message, state: State) -> None:
    text = message.text
    reply = "Now input description if needed or skip"
    await state.set_data({"title": text})

    skip_button = InlineKeyboardButton(text=SKIP_BUTTON_TEXT, callback_data="skip_description")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[skip_button]])

    await message.reply(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    await state.set_state(UserTasks.description)


@router.on_callback_query(filters.regex("skip_description"))
async def skip_description(client: Client, callback: CallbackQuery, state: State) -> None:
    reply = "Input the date when it should be completed. Or skip it"

    skip_button = InlineKeyboardButton(text=SKIP_BUTTON_TEXT, callback_data="skip_complete_till")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[skip_button]])

    await callback.message.edit_text(text=reply, reply_markup=keyboard)
    await state.set_state(UserTasks.complete_till)


@router.on_callback_query(filters.regex("skip_complete_till"))
async def skip_complete_till(client: Client, callback: CallbackQuery, state: State) -> Message:
    state_data = await state.get_data()
    chat_id = str(callback.from_user.id)
    user = await UsersRepository.get_by_chat_id(chat_id=chat_id)
    values = {"user_id": user["id"], "title": state_data["title"], "description": state_data.get("description")}
    await UserTasksRepository.create(values)
    return await task_menu(callback=callback, state=state)


@router.on_message(StateFilter(UserTasks.description))
async def get_description(client: Client, message: Message, state: State) -> Message:
    text = message.text
    reply = ("Input the date when it should be completed. Or skip it.\n"
             "Example of date: 22.11.2024")
    await state.set_data({"description": text})

    skip_button = InlineKeyboardButton(text=SKIP_BUTTON_TEXT, callback_data="skip_complete_till")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[skip_button]])

    await message.reply(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    await state.set_state(UserTasks.complete_till)


@router.on_message(StateFilter(UserTasks.complete_till))
async def get_complete_till(client: Client, message: Message, state: State):
    text = message.text

    try:
        date = datetime.datetime.strptime(text, "%d.%m.%Y")
        now = datetime.datetime.now()
        if date < now:
            reply = "Date is invalid, example of date 22.12.2024. Or skip it"
            skip_button = InlineKeyboardButton(text=SKIP_BUTTON_TEXT, callback_data="skip_complete_till")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[skip_button]])
            return await message.reply(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)

        state_data = await state.get_data()
        chat_id = str(message.from_user.id)
        user = await UsersRepository.get_by_chat_id(chat_id=chat_id)
        values = {
            "user_id": user["id"],
            "title": state_data["title"],
            "complete_till": date,
            "description": state_data.get("description"),
            "status": "PENDING"
        }
        await UserTasksRepository.create(values)

    except Exception as e:
        reply = "Date is invalid, example of date 22.12.2024. Or skip it"
        skip_button = InlineKeyboardButton(text=SKIP_BUTTON_TEXT, callback_data="skip_complete_till")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[skip_button]])

        return await message.reply(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    return await task_menu(message=message, state=state)


@router.on_callback_query(filters.regex("^tasks_list"))
async def get_all_tasks(client: Client, callback: CallbackQuery, state: State) -> Message:
    data = callback.data.split(",")
    chat_id = str(callback.from_user.id)
    page = int(data[1])
    user = await UsersRepository.get_by_chat_id(chat_id=chat_id)
    tasks = await UserTasksRepository.get_all(user_id=user["id"], skip=page-1)

    if len(tasks) == 0:
        return await callback.answer(text="Sorry, no tasks created.", cache_time=2)

    next_tasks = await UserTasksRepository.get_all(user_id=user["id"], skip=page+1)
    reply = ("There are your all created tasks. You may use button  to show the next page\n\n"
             f"<i>Page</i>: {page}")

    keyboard = [
        InlineKeyboardButton(text=f"{t['title']}", callback_data=f"show_task,{t['id']},{page}")
        for t in tasks
    ]
    keyboard = keyboard_cols(keyboard, 2)
    arrow_right_button = InlineKeyboardButton(text=ARROW_RIGHT, callback_data=f"tasks_list,{page + 1}")
    arrow_left_button = InlineKeyboardButton(text=ARROW_LEFT, callback_data=f"tasks_list,{page - 1}")
    back_button = InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="task_menu")

    if len(next_tasks) != 0 and page > 1:
        keyboard.append([arrow_left_button, arrow_right_button])
    elif len(next_tasks) == 0 and page > 1:
        keyboard.append([arrow_left_button])
    elif len(next_tasks) != 0 and page == 1:
        keyboard.append([arrow_right_button])

    keyboard.append([back_button])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

    return await callback.message.edit_text(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.on_callback_query(filters.regex("^show_task"))
async def show_task(client: Client, callback: CallbackQuery, state: State):
    data = callback.data.split(",")
    task_id = int(data[1])
    page = int(data[2])
    task = await UserTasksRepository.get_by_id(task_id)
    status = task["status"].value
    reply = (f"Task: <i>{task['title']}</i>\n"
             f"Description: <i>{task['description'] if task['description'] else 'Empty'}</i>\n\n"
             f"Status: {status}\n"
             f"Complete till: <i>{task['complete_till'] if task['complete_till'] else 'No date'}</i>\n")

    back_button = InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data=f"tasks_list,{page}")
    if status == "pending":
        edit_task_button = InlineKeyboardButton(text="Run task", callback_data=f"edit_task,{task_id},{page},r")
    elif status == "running":
        edit_task_button = InlineKeyboardButton(text="Complete task", callback_data=f"edit_task,{task_id},{page},c")
    else:
        edit_task_button = InlineKeyboardButton(text="Delete task", callback_data=f"edit_task,{task_id},{page},d")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [edit_task_button],
            [back_button]
        ]
    )

    return await callback.message.edit_text(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.on_callback_query(filters.regex("^edit_task"))
async def edit_task(client: Client, callback: CallbackQuery, state: State) -> Message:
    data = callback.data.split(",")
    task_id = int(data[1])
    status = data[3]
    if status == "d":
        await UserTasksRepository.delete(id=task_id)
        return await task_menu(client=client, callback=callback, state=state)

    if status == "r":
        new_status = "RUNNING"
    elif status == "c":
        new_status = "COMPLETED"
    else:
        new_status = "PENDING"

    await UserTasksRepository.update(id=task_id, values={"status": new_status})
    return await show_task(client=client, callback=callback, state=state)
