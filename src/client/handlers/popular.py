from aiogram import types, Dispatcher
from mysql_db.mysql_db import BaseWorking as db
from keyboards import FarmSlider, order_or_holder, cancel
from . import start
from aiogram.dispatcher.filters import Text
from models_client import FarmsteadSearch
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData


cd_popular = CallbackData('cd_popular', 'action', 'page')


async def show_popular(callback: types.CallbackQuery) -> None:
    await callback.answer()   
    await callback.message.answer('У нас собраны более 1000 агроусадеб. Вы можете ознакомиться с ними ниже.')
    slider = FarmSlider(cd_slider = cd_popular, farm_list=await db.get_popular(), callback=callback)
    await slider.get_slider()


async def process_slider(callback: types.CallbackQuery, callback_data: dict) -> None:
    await callback.answer()
    slider = FarmSlider(cd_slider = cd_popular, callback=callback, callback_data=callback_data, farm_list=await db.get_popular())
    selected, data = await slider.process_farm_slider()
    if selected:
        names = data[1]
        await callback.message.answer(f'Агроусадьба "<i><b>{names[int(data[3])]}</b></i>".',
                                      parse_mode='html',
                                      reply_markup=await order_or_holder(data[1][int(data[3])]))


async def make_order(callback: types.CallbackQuery, state: FSMContext):
    name = callback.data.split(':')[1]
    async with state.proxy() as data:
            data['name'] = name
    await FarmsteadSearch.adults_number.set()
    await callback.message.answer(f'⌛ Заказ места в агроусадьбе <i><b>"{name}"</b></i>.\n\n'
                                  'Сколько у вас будет взрослых? Дайте ответ цифрой:',
                                  reply_markup=cancel, parse_mode='html')


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start.send_cancel, commands=['cancel'], state='*')

    dp.register_callback_query_handler(show_popular, text='show_popular')

    dp.register_callback_query_handler(make_order, Text(startswith='make_order:'))
 
    dp.register_callback_query_handler(show_popular, text='write_to_holder')
    dp.register_callback_query_handler(process_slider, cd_popular.filter())