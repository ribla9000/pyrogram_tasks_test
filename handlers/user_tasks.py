import datetime
from core.config import BACK_BUTTON_TEXT, SKIP_BUTTON_TEXT, ARROW_LEFT, ARROW_RIGHT
from pyrogram import filters
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
async def task_menu(callback: Union[CallbackQuery, None], message: Union[Message, None] = None):
    reply = "There is a task menu"

    back_button = InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="start")
    create_task_button = InlineKeyboardButton(text="Создать задача", callback_data="create_task")
    show_all_tasks_button = InlineKeyboardButton(text="Смотреть все задачи", callback_data="tasks_list,1")
    show_by_filter = InlineKeyboardButton(text="Смотреть по фильтру", callback_data="tasks_filtered,1")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [create_task_button],
            [show_all_tasks_button],
            [show_by_filter],
            [back_button]
        ]
    )

    if message is not None:
        return await message.reply(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    elif callback is not None:
        return await callback.message.edit_text(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.on_callback_query(filters.regex("create_task"))
async def create_task(callback: CallbackQuery, state: State) -> Message:
    reply = "Please name this task. This name will be displayed in menu as a button"
    await state.set_state(UserTasks.title)

    back_button = InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="task_menu")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    return await callback.message.edit_text(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.on_message(StateFilter(UserTasks.title))
async def get_title(message: Message, state: State) -> Message:
    text = message.text
    reply = "Now input description if needed or skip"
    await state.set_data({"title": text})

    skip_button = InlineKeyboardButton(text=SKIP_BUTTON_TEXT, callback_data="skip_description")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[skip_button]])

    await state.set_state(UserTasks.description)
    return await message.edit_text(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.on_callback_query(filters.regex("skip_description"))
async def skip_description(callback: CallbackQuery, state: State) -> Message:
    reply = "Input the date when it should be completed. Or skip it"
    await state.set_state(UserTasks.complete_till)

    skip_button = InlineKeyboardButton(text=SKIP_BUTTON_TEXT, callback_data="skip_complete_till")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[skip_button]])

    return await callback.message.edit_text(text=reply, reply_markup=keyboard)


@router.on_callback_query(filters.regex("skip_complete_till"))
async def skip_complete_till(callback: CallbackQuery, state: State) -> Message:
    state_data = await state.get_data()
    chat_id = str(callback.from_user.id)
    user = await UsersRepository.get_by_chat_id(chat_id=chat_id)
    values = {"user_id": user["id"], "title": state_data["title"], "description": state_data.get("description")}
    await UserTasksRepository.create(values)
    return await task_menu(callback=callback, state=state)


@router.on_message(StateFilter(UserTasks.description))
async def get_description(message: Message, state: State):
    text = message.text
    reply = ("Input the date when it should be completed. Or skip it.\n"
             "Example of date: 22.11.2024")
    await state.set_data({"description": text})
    await state.set_state(UserTasks.complete_till)

    skip_button = InlineKeyboardButton(text=SKIP_BUTTON_TEXT, callback_data="skip_complete_till")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[skip_button]])

    return await message.reply(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.on_message(StateFilter(UserTasks.complete_till))
async def get_complete_till(message: Message, state: State):
    text = message.text

    try:
        date = datetime.datetime.strptime(text, "%Y-%m-%d 00:00:00")
        state_data = await state.get_data()
        chat_id = str(message.from_user.id)
        user = await UsersRepository.get_by_chat_id(chat_id=chat_id)
        values = {
            "user_id": user["id"],
            "title": state_data["title"],
            "complete_till": date,
            "description": state_data.get("description")
        }
        await UserTasksRepository.create(values)

    except Exception as e:
        reply = "Date is invalid, example of date 22.12.2024. Or skip it"
        skip_button = InlineKeyboardButton(text=SKIP_BUTTON_TEXT, callback_data="skip_complete_till")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[skip_button]])

        return await message.reply(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    return await task_menu(message=message, state=State)


@router.on_callback_query(filters.regex("^tasks_list"))
async def get_all_tasks(callback: CallbackQuery) -> Message:
    data = callback.data.split(",")
    chat_id = str(callback.from_user.id)
    page = int(data[1]) - 1
    user = await UsersRepository.get_by_chat_id(chat_id=chat_id)
    tasks = await UserTasksRepository.get_all(user_id=user["id"], skip=page)

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

    if len(next_tasks) != 0 and page > 0:
        keyboard.append([arrow_left_button, arrow_right_button])
    elif len(next_tasks) == 0 and page > 0:
        keyboard.append([arrow_left_button])
    elif len(next_tasks) != 0 and page == 0:
        keyboard.append([arrow_right_button])

    keyboard.append([back_button])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

    return await callback.message.edit_text(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.on_callback_query(filters.regex("^show_task"))
async def show_task(callback: CallbackQuery):
    data = callback.data.split(",")
    task_id = int(data[1])
    page = int(data[2])
    task = await UserTasksRepository.get_by_id(task_id)
    reply = (f"Task: <i>{task['title']}</i>\n"
             f"Description: <i>{task['description'] if task['description'] else 'Empty'}</i>\n\n"
             f"Status: {task['status']}\n"
             f"Complete till: <i>{task['complete_till'] if task['complete_till'] else 'No date'}</i>\n")

    back_button = InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data=f"tasks_list,{page}")
    if task["status"] == "pending":
        edit_task_button = InlineKeyboardButton(text="Run task", callback_data=f"edit_task,{task_id},r")
    elif task["status"] == "running":
        edit_task_button = InlineKeyboardButton(text="Complete task", callback_data=f"edit_task,{task_id},c")
    else:
        edit_task_button = InlineKeyboardButton(text="Delete task", callback_data=f"edit_task,{task_id},d")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [edit_task_button],
            [back_button]
        ]
    )

    return await callback.message.edit_text(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.on_callback_query(filters.regex("^edit_task"))
async def edit_task(callback: CallbackQuery):
    data = callback.data.split(",")
    task_id = int(data[1])
    status = data[2]
    if status == "d":
        await UserTasksRepository.delete(id=task_id)
        return await task_menu(callback=callback)

    if status == "r":
        new_status = "running"
    elif status == "c":
        new_status = "completed"
    else:
        new_status = "pending"

    await UserTasksRepository.update(id=task_id, values={"status": new_status})
    return await show_task(callback=callback)
