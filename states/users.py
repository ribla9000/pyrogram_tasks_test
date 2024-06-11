from pyrogram_patch.fsm import StateItem, StatesGroup


class UsersState(StatesGroup):
    nickname = StateItem()
    login = StateItem()
    login2 = StateItem()

