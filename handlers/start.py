from core.config import NONE_FUNCTION
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram_patch.router import Router
from pyrogram_patch.fsm.states import State
from pyrogram_patch.fsm.filter import StateFilter
from states.users import UsersState
from repository.database.users import UsersRepository
from typing import Union


router = Router()


async def create_user(message: Message) -> int:
    chat_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    user_values = {
        "first_name": first_name if first_name is not None else "",
        "last_name": last_name if last_name is not None else "",
        "username": message.from_user.username,
        "chat_id": chat_id
    }
    user_id = await UsersRepository.create(user_values)
    return user_id


async def start_menu(message: Union[Message, None] = None,
                     callback: Union[CallbackQuery, None] = None,
                     state: Union[State, None] = None) -> Union[None, Message]:
    await state.finish()
    chat_id = str(message.from_user.id if message is not None else callback.from_user.id)
    user = await UsersRepository.get_by_chat_id(chat_id=chat_id)

    if user is None:
        user_id = await create_user(message)
        user = await UsersRepository.get_by_id(id=user_id)

    if user["nickname"] is None:
        reply = ("Please give yourself a Name|Fullname|Nickname\n"
                 "<i>For example: MaxIm</i> or <i>John</i>, or <i>Smith John</i>\n")
        await message.reply(text=reply, parse_mode=ParseMode.HTML)
        await state.set_state(UsersState.nickname)
        return None

    task_menu_button = InlineKeyboardButton(text="Меню задач", callback_data="task_menu")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[task_menu_button]])

    reply = ("Hi there! Nice to meet you!\n"
             f"Name: <i>{user['nickname']}</i>\n"
             f"Login: <i>{user['login_name']}</i>\n")

    if message is not None:
        return await message.reply(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    else:
        return await callback.message.edit_text(text=reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.on_message(filters.command(["start"]))
async def start_on_command(message: Message, state: State):
    await state.finish()
    return await start_menu(message=message, state=state)


@router.on_callback_query((filters.CallbackQuery, filters.regex("^start")))
async def start_on_callback(callback: CallbackQuery, state: State):
    await state.finish()
    return await start_menu(callback=callback)


@router.on_callback_query(filters.regex(NONE_FUNCTION))
async def none_function(callback: CallbackQuery, state: State):
    await state.finish()
    return await callback.answer()


@router.on_message((filters.Message, StateFilter(UsersState.nickname)))
async def get_nickname(message: Message, state: State) -> Message:
    text = message.text
    await state.set_data({"nickname": text})
    reply = "Thx. Please now input your login. That's need for the log-in"
    await state.set_state(UsersState.login_name)
    return await message.reply(text=reply, parse_mode=ParseMode.HTML)


@router.on_message((filters.Message, StateFilter(UsersState.login_name)))
async def get_login_name(message: Message, state: State) -> Message:
    text = message.text
    chat_id = str(message.from_user.id)
    user = await UsersRepository.get_by_chat_id(chat_id)
    await state.set_data({"login_name": text})
    state_data = await state.get_data()
    values = {"login_name": state_data["login_name"], 'nickname': state_data["nickname"]}
    await UsersRepository.update(id=user["id"], values=values)
    await state.finish()
    return await start_menu(message=message, state=state)
