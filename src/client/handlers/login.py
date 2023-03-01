from aiogram import types, Dispatcher
from mysql_db.mysql_db import BaseWorking as db
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from models_client import ClientRegistration, ClientLogin
from keyboards import cancel, start_keyboard, get_start
from . import start


# Client registration ----------

async def register(message: types.Message):
    await ClientRegistration.client_login.set()
    await message.answer('Введите ваш новый логин:', reply_markup=cancel)


async def set_login(message: types.Message, state: FSMContext):
    client = ClientRegistration(login=message.text, message=message)
    if await client.check_login():
        async with state.proxy() as data:
            data['login'] = message.text
        await ClientRegistration.client_password.set()
        await message.answer('Введите пароль:', reply_markup=cancel)


async def set_password(message: types.Message, state: FSMContext):
    client = ClientRegistration(password=message.text, message=message)
    if await client.check_password():
        async with state.proxy() as data:
            data['password'] = message.text
        await message.delete()
        await ClientRegistration.client_confirm_password.set()
        await message.answer('Повторите пароль:', reply_markup=cancel)


async def set_confirm_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        client = ClientRegistration(password = data['password'], confirm_password=message.text, message=message)
        if await client.check_confirm_password():
            await db.create_new_client(data)
            await message.delete()
            await state.finish()
            await db.change_client_enter(data['login'], message.from_user.id)
            await message.answer('Регистрация успешно завершена.', reply_markup=await get_start(login=await db.get_client_login(message.from_user.id), user_id=message.from_user.id))
            await message.answer('Где бы вам хотелось отдохнуть?', reply_markup=start_keyboard)


# Client login/logout ----------

async def login(message: types.Message):
    await ClientLogin.client_login.set()
    await message.answer('Введите логин:', reply_markup=cancel)


async def set_login_enter(message: types.Message, state: FSMContext):
    client = ClientLogin(login=message.text, message=message)
    if await client.check_login():
        async with state.proxy() as data:
            data['client_login'] = client.get_login
            await ClientLogin.client_password.set()
            await message.answer("Введите пароль:", reply_markup=cancel)


async def set_password_enter(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        client = ClientLogin(login=data['client_login'], password=message.text, message=message)
        if await client.check_password():
            data['client_password'] = client.get_password
            await state.finish()
            await db.change_client_enter(data['client_login'], message.from_user.id)
            await message.answer('✅ Выполнен вход.', reply_markup=await get_start(login=await db.get_client_login(message.from_user.id), user_id=message.from_user.id))
            await message.delete()
            await message.answer('Где бы вам хотелось отдохнуть?', reply_markup=start_keyboard)


async def logout(message: types.Message):
    await db.logout_client(message.from_user.id)
    await message.answer('✔ Выполнен выход.', reply_markup=await get_start(login=await db.get_client_login(message.from_user.id), user_id=message.from_user.id))
    await message.answer('Где бы вам хотелось отдохнуть?', reply_markup=start_keyboard)


def register_handlers(dp: Dispatcher):
    
    dp.register_message_handler(start.send_cancel, commands=['cancel'], state='*')

    dp.register_message_handler(register, Text(equals='Регистрация'))
    dp.register_message_handler(login, Text(equals='Вход'))
    dp.register_message_handler(logout, Text(equals='Выход'))

    dp.register_message_handler(set_login, state=ClientRegistration.client_login)
    dp.register_message_handler(set_password, state=ClientRegistration.client_password)
    dp.register_message_handler(set_confirm_password, state=ClientRegistration.client_confirm_password)

    dp.register_message_handler(set_login_enter, state=ClientLogin.client_login)
    dp.register_message_handler(set_password_enter, state=ClientLogin.client_password)

    dp.register_callback_query_handler(start.cancel_everything, text='cancel', state='*')