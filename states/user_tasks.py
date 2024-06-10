from pyrogram_patch.fsm import StateItem, StatesGroup


class UserTasks(StatesGroup):
    title = StateItem()
    description = StateItem()
    complete_till = StateItem()
