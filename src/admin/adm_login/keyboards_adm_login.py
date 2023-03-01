from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from mysql_db.mysql_db import BaseWorking as db


async def start_admin(user_id):
    k = InlineKeyboardMarkup(row_width=1)
    if not await db.check_if_admin_enter(user_id):
        return k.add(InlineKeyboardButton(text="Войти", callback_data="adm_enter")).\
                 add(InlineKeyboardButton(text="Регистрация", callback_data="adm_registration"))
    else:
        return k.add(load_info).\
                 add(InlineKeyboardButton(text="Выйти", callback_data="adm_exit"))


start_holder = InlineKeyboardMarkup(row_width=1)
load_info = InlineKeyboardButton(text='Добавить агроусадьбу', callback_data='load_info')
back_to_menu = InlineKeyboardButton(text='Назад', callback_data='back_to_main')
start_holder.add(load_info, back_to_menu)


cancel_login = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text='Отмена', callback_data='cancel_admin_login')
)


start_holder = InlineKeyboardMarkup(row_width=1)
load_info = InlineKeyboardButton(text='Добавить агроусадьбу', callback_data='load_info')
back_to_menu = InlineKeyboardButton(text='Назад', callback_data='back_to_main')
start_holder.add(load_info, back_to_menu)


cancel_load = InlineKeyboardMarkup(row_width=1)
cancel= InlineKeyboardButton(text='Отмена', callback_data='cancel_load')
cancel_load.add(cancel)