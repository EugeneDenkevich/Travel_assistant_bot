from aiogram import types, Dispatcher
from create_bot_adm import bot_adm
from decimal import Decimal
from aiogram.dispatcher import FSMContext
from models_adm import Farmstead
from mysql_db import BaseWorking as db
import traceback
from adm_login.keyboards_adm_login import cancel_load
from adm_login.adm_login_handlers import go_back, send_start


async def farm_load(callback: types.CallbackQuery):
    if not await db.check_if_admin_enter(callback.from_user.id):
        await go_back(callback, s="Сначала войдите в свой аккаунт")
        await callback.answer()
    else:
        await Farmstead.name.set()
        await callback.message.answer('<b><i>Пожалуйста, введите название агроусадьбы:</i></b>', parse_mode='html', reply_markup=cancel_load)
        await callback.answer()


async def check_farm_name(message_text):
    for i in '/\:*?"><|':
        if i in message_text:
            return True
    return False

async def set_name(message: types.Message, state: FSMContext):
    if await check_farm_name(message.text):
        await message.answer('Нельзя использовать символы /\:*?"><|\nПопробуйте ещё раз:', reply_markup=cancel_load)
    else:
        if message.text.capitalize().strip() not in await db.get_farm_names():
            async with state.proxy() as data:
                data['name'] = message.text.capitalize().strip()
            await Farmstead.next()
            await message.answer('<b><i>Введите адрес:</i></b>', parse_mode='html', reply_markup=cancel_load)
        else:
            await message.answer('<b><i>Такое название уже существует. Введите другое название.</i></b>', parse_mode='html', reply_markup=cancel_load)


async def set_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
    await Farmstead.next()
    await message.answer('<b><i>Загрузите фотографию вашей агроусадьбы. Просто перетащите её сюда. </i></b>', parse_mode='html', reply_markup=cancel_load)


async def load_photo(message: types.Message, state: FSMContext):
    if message.photo:
        holder_login = await db.get_current_holder_login(message.from_user.id)
        farm_name = ''
        file_path = ''
        async with state.proxy() as data:
            farm_name = data['name']
            file_path = f'src/farmsteads/{holder_login}/{farm_name}/photo/{message.photo[-1].file_id}.jpg'
            data['photo'] = file_path
        await message.photo[-1].download(destination_file=file_path)
        await Farmstead.next()
        await message.answer('<b><i>К чему относится ваша агроусадьба?\nПример: Беловежская Пуща, Браславские озёра...)</i></b>', parse_mode='html', reply_markup=cancel_load)
    elif message.document:
        await message.answer('<b><i>Загрузите файл как фото, а не как документ (с сжатием изображения).</i></b>', parse_mode='html', reply_markup=cancel_load)
    else:
        await message.answer('<b><i>Загрузите фото, пожалуйста</i></b>', parse_mode='html', reply_markup=cancel_load)


async def set_destination(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['destination'] = message.text
    await Farmstead.next()
    await message.answer('<b><i>Сколько у вас мест для проживания?</i></b>', parse_mode='html', reply_markup=cancel_load)


async def set_rooms_number(message: types.Message, state = FSMContext):
    try:
        async with state.proxy() as data:
            data['rooms_number'] = int(message.text)
        await Farmstead.next()
        await message.answer('<b><i>Какие услуги вы предоставляете?</i></b>', parse_mode='html', reply_markup=cancel_load)
    except ValueError:
        await message.answer('<b><i>Введите <u>цифры</u>, пожалуйста.</i></b>', parse_mode='html', reply_markup=cancel_load)


async def set_services(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['services'] = message.text
    await Farmstead.next()
    await message.answer('<b><i>Укажите цену за сутки</i></b>', parse_mode='html', reply_markup=cancel_load)


async def set_price(message: types.Message, state = FSMContext):
    try:
        async with state.proxy() as data:
            data['price'] = Decimal(message.text)
        await Farmstead.next()
        await message.answer('<b><i>Есть ли у вас поблизости водоём или озеро? Введите "да" или "нет"</i></b>', parse_mode='html', reply_markup=cancel_load)
    except ArithmeticError:
        await message.answer('<b><i>Введите <u>цифры</u>, пожалуйста.</i></b>', parse_mode='html', reply_markup=cancel_load)


async def set_is_water_near(message: types.Message, state = FSMContext):
    if message.text == 'да' or message.text == 'нет':
        async with state.proxy() as data:
            data['is_water_near'] = message.text
        await Farmstead.next()
        await message.answer('<b><i>Опишие ваши уникальные особенности.</i></b>', parse_mode='html', reply_markup=cancel_load)
    else:
        await message.answer('<b><i>Введите либо <u>да</u>, либо <u>нет</u>, пожалуйста.</i></b>', parse_mode='html', reply_markup=cancel_load)


async def set_unique_services(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['unique_services'] = message.text
    await Farmstead.contact_phone.set()
    await message.answer('<b><i>Контактные телефоны для заказов, через запятую:</i></b>', parse_mode='html', reply_markup=cancel_load)


async def set_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['contact_phones'] = message.text
    await Farmstead.contact_email.set()
    await message.answer('<b><i>Электронная почта для заказов:</i></b>', parse_mode='html', reply_markup=cancel_load)


async def set_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['contact_email'] = message.text
    await Farmstead.gps_number.set()
    await message.answer('<b><i>Где находится агроусадьба? Подойдёт ссылка из google карт.:</i></b>', parse_mode='html', reply_markup=cancel_load)


async def set_gps(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gps_number'] = message.text
    await Farmstead.website_link.set()
    await message.answer('<b><i>Введите ссылку на ваш сайт:</i></b>', parse_mode='html', reply_markup=cancel_load)


async def set_website(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['website_link'] = message.text
            data['holder_login'] = await db.get_current_holder_login(message.from_user.id)
            
        await db.add_new_farmstead(state)
        await message.answer('<b><i>Спасибо! Данные успрешно добавлены.</i></b>', parse_mode='html')
        await state.finish()
        await send_start(message)
    except Exception:
        await bot_adm.send_message(message.from_user.id, '<b><i>Ошибка добавления данных. Попробуйте снова.</i></b>', parse_mode='html')
        print(traceback.format_exc())
        await state.finish()


async def cancel_loads(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await callback.answer('Операция отменена')
    await go_back(callback)


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(set_name, state=Farmstead.name)
    dp.register_message_handler(set_address, state=Farmstead.address)
    dp.register_message_handler(load_photo, state=Farmstead.photo, content_types=types.ContentTypes.ANY)
    dp.register_message_handler(set_destination, state=Farmstead.destination)
    dp.register_message_handler(set_rooms_number, state=Farmstead.rooms_number)
    dp.register_message_handler(set_services, state=Farmstead.services)
    dp.register_message_handler(set_price, state=Farmstead.price)
    dp.register_message_handler(set_is_water_near, state=Farmstead.is_water_near)
    dp.register_message_handler(set_unique_services, state=Farmstead.unique_services)
    dp.register_message_handler(set_phone_number, state=Farmstead.contact_phone)
    dp.register_message_handler(set_email, state=Farmstead.contact_email)
    dp.register_message_handler(set_gps, state=Farmstead.gps_number)
    dp.register_message_handler(set_website, state=Farmstead.website_link)
    dp.register_callback_query_handler(farm_load, text='load_info', state=None)
    dp.register_callback_query_handler(cancel_loads, text='cancel_load', state='*')