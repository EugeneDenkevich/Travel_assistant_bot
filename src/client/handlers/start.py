from aiogram import types, Dispatcher
from mysql_db.mysql_db import BaseWorking as db
from keyboards import start_keyboard, get_start
from models_client import ClientName
from aiogram.dispatcher import FSMContext
from . import login, popular, place, search
from aiogram.dispatcher.filters import Text


# Start menu ----------

async def send_start(message: types.Message):
    client = ClientName(message=message)
    await message.answer(f'Здравствуйте, {await client.check_name()}.',
                         reply_markup = await get_start(login=
                         await db.get_client_login(message.from_user.id),
                         user_id=message.from_user.id))
    await message.answer('Где бы вам хотелось отдохнуть?', reply_markup=start_keyboard)


# Client feedback ----------

async def feedback(message: types.Message):
    await message.answer('Обратная связь с разработчиками')


# Cancel/No/Help ----------

async def cancel_everything(callback: types.CallbackQuery, state: FSMContext):
    await db.drop_criteria(callback.from_user.id)
    await db.drop_checkbox(callback.from_user.id)
    await callback.answer()
    current_state = await state.get_state()
    if current_state == None:
        await callback.answer()
        return
    await state.finish()
    await callback.message.answer('Операция отменена./start', reply_markup=await get_start(login=
                         await db.get_client_login(callback.from_user.id),
                         user_id=callback.from_user.id))


async def send_cancel(message: types.Message, state: FSMContext):
    await db.drop_criteria(message.from_user.id)
    await db.drop_checkbox(message.from_user.id)
    current_state = await state.get_state()
    if current_state == None:
        await message.answer('Сначала нажмите /start')
        return
    await state.finish()
    await message.answer('Операция отменена./start', reply_markup=await get_start(login=
                         await db.get_client_login(message.from_user.id),
                         user_id=message.from_user.id))


async def give_help(message: types.Message):
    await message.answer('Сначала нажмите /start')


async def give_warning(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer('Эта операция неактивна')
    else:
        await callback.answer('Закончите текущую операцию, либо нажмите /cancel')


def register_handlers_client(dp: Dispatcher):

    dp.register_message_handler(send_start, commands=['start'])
    dp.register_message_handler(send_cancel, commands=['cancel'], state='*')
    dp.register_message_handler(feedback, Text(equals='Обратная связь'))  
    dp.register_callback_query_handler(cancel_everything, text='cancel', state='*')
    
    login.register_handlers(dp)
    popular.register_handlers(dp)
    place.register_handlers(dp)
    search.register_handlers(dp)

    dp.register_message_handler(give_help)
    dp.register_callback_query_handler(give_warning, state='*')



"""
Далее:

- Словарь поиска должен формировать поисковой слайдер: выгрузить словарь либо в таблицу, либо в файл JSON
  дальше взять эти данные для формирования слайдера, либо обновить их, добавив ещё критериев через инлайн-запрос.
- Попробовать очищение БД через создание ещё одной БД с чекбоксами и инфой по критериям.
  ИЛИ правильнее будет сделать списки regions, criteria и т. п. отдельными таблицами в БД и ссылаться на всё это
  дело чере JOIN-ы.
- Добавить проверку на валидность при вводе бюджета
- В "Написать владельцу" выдаёт слайдер - исправить

- 

"""