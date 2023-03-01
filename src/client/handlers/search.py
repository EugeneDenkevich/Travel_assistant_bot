from aiogram import types, Dispatcher
from keyboards import Checkbox
from models_client import FarmsteadSearch
from aiogram.dispatcher import FSMContext
from keyboards import cancel, after_criteria, FarmSlider, order_or_holder
from .aiogram_calendar.simple_calendar import SimpleCalendar
from mysql_db.mysql_db import BaseWorking as db
from aiogram.utils.callback_data import CallbackData
from checkboxes import regions, criteria, more_criteria


cd_search = CallbackData('cd_search', 'action', 'page')


async def show_search(callback: types.CallbackQuery):
    await callback.answer()
    box = Checkbox(callback, *regions[0], **regions[1])
    await box.check_box()
    await FarmsteadSearch.regions.set()
    await callback.message.answer('В какой области вы планируете отдохнуть?', reply_markup=await box.get_box())


async def set_regions(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    box = Checkbox(callback, callback_data, *regions[0], **regions[1])
    res = await box.process_box()
    if res != []:
        async with state.proxy() as data:
            data['regions'] = res
        await FarmsteadSearch.adults_number.set()
        await callback.message.answer(f"<b><i>Вы выбрали: {data['regions']}</i></b>", parse_mode='html')
        await callback.message.answer('Сколько у вас будет взрослых? Дайте ответ цифрой:', reply_markup=cancel)


async def set_budget(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['budget'] = message.text
    await FarmsteadSearch.start_date.set()
    await message.answer('В какой период времени планируете отдых? Выберете день заезда:',
                                    reply_markup=await SimpleCalendar().start_calendar())


async def set_criteria(callback: types.CallbackQuery, callback_data: dict,  state: FSMContext):
    box = Checkbox(callback, callback_data, *criteria[0], **criteria[1])
    res = await box.process_box()
    if res != []:
        async with state.proxy() as data:
            data['criteria'] = res
            await db.get_criteria_table(callback.from_user.id, data)
        await state.finish()
        criteria_base = await db.get_criteria(callback.from_user.id) # Получаем критерии для дальнейшей выборки
        n = 100 # Колличество усадеб, подходящих по критериям
        await callback.message.answer(f'Для вас есть {n} предложений.', reply_markup=after_criteria)


async def get_offers(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        criteria_base = await db.get_criteria(callback.from_user.id) # Получаем критерии для дальнейшей выборки
        await db.drop_criteria(callback.from_user.id)
        user_id = callback.message.from_user.id
        slider = FarmSlider(cd_slider = cd_search,
                            farm_list=await db.get_farm_by_criteria(user_id),
                            callback=callback)
        await slider.get_slider()
    except Exception:
        await callback.answer('Эта операция неактивна')

async def process_offers_slider(callback: types.CallbackQuery, callback_data: dict) -> None:
    await callback.answer()
    user_id = callback.message.from_user.id
    slider = FarmSlider(cd_slider = cd_search,
                        callback=callback,
                        callback_data=callback_data,
                        farm_list=await db.get_farm_by_criteria(user_id))
    selected, data = await slider.process_farm_slider()
    if selected:
        names = data[1]
        await callback.message.answer(f'Агроусадьба "<i><b>{names[int(data[3])]}</b></i>".',
                                      parse_mode='html',
                                      reply_markup=await order_or_holder(data[1][int(data[3])]))
        

async def add_criteria(callback: types.CallbackQuery) -> None:
    try:
        box = Checkbox(callback, None, *more_criteria[0], **more_criteria[1])
        await FarmsteadSearch.more_criteria.set()
        await callback.message.answer('Давайте еще конкретизируем запрос:', reply_markup=await box.get_box())
    except Exception as e:
        print('error', e)
        await callback.answer('Эта операция неактивна')


async def set_more_criteria(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    box = Checkbox(callback, callback_data, *more_criteria[0], **more_criteria[1])
    res = await box.process_box()
    if res != []:
        await db.update_criteria_table(callback.from_user.id, res)
        await state.finish()
        criteria_base = await db.get_criteria(callback.from_user.id) # Получаем критерии для дальнейшей выборки
        n = 100 # Колличество усадеб, подходящих по критериям. Вычисляется по критериям.
        await callback.message.answer(f'Для вас есть {n} предложений.', reply_markup=after_criteria)
 

def register_handlers(dp: Dispatcher):

    dp.register_callback_query_handler(show_search, text='show_search')
    dp.register_callback_query_handler(set_regions, Checkbox.call_data.filter(), state=FarmsteadSearch.regions)
    dp.register_callback_query_handler(get_offers, text='watch_choiсe')
    dp.register_callback_query_handler(add_criteria, text='add_criteria')
    dp.register_callback_query_handler(set_more_criteria, Checkbox.call_data.filter(), state=FarmsteadSearch.more_criteria)

    
    dp.register_callback_query_handler(process_offers_slider, cd_search.filter())