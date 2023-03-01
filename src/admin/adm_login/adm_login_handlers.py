from aiogram import types, Dispatcher
from mysql_db.mysql_db import BaseWorking as db
from .keyboards_adm_login import start_admin, cancel_login
from models_adm import AdmPassword
from aiogram.dispatcher import FSMContext
from admin_registration import admin_registration_handlers as adm_reg


async def send_help(message: types.Message):
    await message.answer('Нажмите /start, чтобы начать')


async def send_start(message: types.Message, s="Привет! Что будем делать?"):
    await message.answer(s, reply_markup=await start_admin(message.from_user.id))


async def enter_login(callback: types.CallbackQuery):
    if await db.check_if_admin_enter(callback.from_user.id):
        await go_back(callback, s="Вы уже вошли!")
        await callback.answer()
    else:
        await AdmPassword.holder_login.set()
        await callback.message.answer('Введите свой логин', reply_markup=cancel_login)
        await callback.answer()


async def check_login(message: types.Message, state: FSMContext):
    try:
        if await db.check_adm_login(message.text):
            async with state.proxy() as data:
                data['holder_login'] = message.text
            await AdmPassword.admin_password.set()
            await message.answer('Введите свой пароль', reply_markup=cancel_login)
        else:
            await message.answer('Неверный логин. Попробуйте ещё раз:', reply_markup=cancel_login)
    except:
        await message.answer('<b><i>Ошибка входа. Попробуйте ещё раз.</i></b>', parse_mode='html')
        await send_start(message)


async def check_holder_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if await db.check_holder_password(message.text, data['holder_login']):
            await message.delete()
            await db.set_current_wtiter(message.from_user.id, data['holder_login'])
            await db.change_holder_enter(data['holder_login'])
            await state.finish()
            await message.answer(f'Добро пожаловать!', reply_markup=await start_admin(message.from_user.id))
        else:
            await message.answer('Неверный пароль, попробуйте ещё раз', reply_markup=cancel_login)


async def cancel_admin_login(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback.message.answer("Привет! Что будем делать?", reply_markup=await start_admin(callback.from_user.id))
        await callback.answer()
    else:
        await callback.answer("Операция отменена")
        await state.finish()
        await callback.message.answer("Привет! Что будем делать?", reply_markup=await start_admin(callback.from_user.id))
        await callback.answer()


async def go_back(callback: types.CallbackQuery, s="Что будем делать?"):
    await callback.message.edit_text(s, reply_markup=await start_admin(callback.from_user.id))
    await callback.answer()


async def admin_exit(callback: types.CallbackQuery):
    await db.change_holder_enter_exit(callback.from_user.id)
    await db.reset_current_writer(callback.from_user.id)
    await callback.message.answer("Что будем делать?", reply_markup=await start_admin(callback.from_user.id))
    await callback.answer()


def register_handlers_admin_login(dp: Dispatcher):
    dp.register_message_handler(send_start, commands=['start'])
    dp.register_callback_query_handler(enter_login, text='adm_enter')
    dp.register_message_handler(check_login, state=AdmPassword.holder_login)
    dp.register_callback_query_handler(go_back, text='back_to_main')
    dp.register_message_handler(check_holder_password, state=AdmPassword.admin_password)
    dp.register_callback_query_handler(cancel_admin_login, text='cancel_admin_login', state='*')
    dp.register_callback_query_handler(admin_exit, text="adm_exit")
    dp.register_message_handler(send_help)
    dp.register_callback_query_handler(adm_reg.start_holder_registration, text="adm_registration")
    adm_reg.register_handlers_admin_registration(dp)