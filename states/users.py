from pyrogram_patch.fsm import StateItem, StatesGroup


class UsersState(StatesGroup):
    nickname = StateItem()
    login_name = StateItem()
