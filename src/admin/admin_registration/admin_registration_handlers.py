from aiogram import types, Dispatcher
from mysql_db.mysql_db import BaseWorking as db
from models_adm import AdmPassword
from aiogram.dispatcher import FSMContext
from adm_login.keyboards_adm_login import cancel_login
from adm_login import adm_login_handlers as adm_log


async def start_holder_registration(callback: types.CallbackQuery):
    if await db.check_if_admin_enter(callback.from_user.id):
        await adm_log.go_back(callback, s="Вы уже вошли!")
        await callback.answer()
    else:
        await AdmPassword.holder_login_set.set()
        await callback.message.answer('Введите новый логин:', reply_markup=cancel_login)
        await callback.answer()


async def set_holder_login(message: types.Message, state: FSMContext):
    if not await db.check_adm_login(message.text):
        async with state.proxy() as data:
            data['holder_login_set'] = message.text
        await AdmPassword.new_admin_password.set()
        await message.answer('Введите новый пароль:', reply_markup=cancel_login)
    else:
        await message.answer('Такой логин уже существует. Придумайте новый:', reply_markup=cancel_login)


async def set_holder_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['admin_password'] = message.text
    await AdmPassword.new_admin_password_repead.set()
    await message.answer('Повторите пароль:', reply_markup=cancel_login)


async def finish_holder_register(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data['admin_password'] == message.text:
            await db.create_new_holder(message.from_user.id, data['admin_password'], data['holder_login_set'])
            await db.change_holder_enter(data['holder_login_set'])
            await db.set_current_wtiter(message.from_id, data['holder_login_set'])
            await state.finish()
            await adm_log.send_start(message)
        else:
            await message.answer('Пароли не совпадают. Попробуйте ещё раз:', reply_markup=cancel_login)


def register_handlers_admin_registration(dp: Dispatcher):
    dp.register_message_handler(set_holder_login, state=AdmPassword.holder_login_set)
    dp.register_message_handler(set_holder_password, state=AdmPassword.new_admin_password)
    dp.register_message_handler(finish_holder_register, state=AdmPassword.new_admin_password_repead)
    dp.register_callback_query_handler(adm_log.cancel_admin_login, text='cancel_admin_login', state='*')