from aiogram import types, Dispatcher
from models_client import FarmsteadSearch, CheckingFarm
from aiogram.dispatcher import FSMContext
from keyboards import cancel, is_it_correct
from .aiogram_calendar.simple_calendar import calendar_callback as simple_cal_callback, SimpleCalendar
from mysql_db.mysql_db import BaseWorking as db
from . import search 
from keyboards import Checkbox


async def show_place(callback: types.CallbackQuery):
    await callback.answer()
    await FarmsteadSearch.name.set()
    await callback.message.answer('Введите название:', reply_markup=cancel)
    await callback.answer()


async def set_name(message: types.Message, state: FSMContext):
    farm = CheckingFarm(name=message.text, message=message)
    if await farm.check_name():
        async with state.proxy() as data:
            data['name'] = farm.name
        await FarmsteadSearch.adults_number.set()
        await message.answer('Сколько у вас будет взрослых? Дайте ответ цифрой:', reply_markup=cancel)


async def set_adult(message: types.Message, state: FSMContext):
    farm = CheckingFarm(value=message.text, message=message)
    if await farm.check_number():
        async with state.proxy() as data:
            data['adults_number'] = farm.value
        await FarmsteadSearch.child_number.set()
        await message.answer('Сколько у вас будет детей (до ... лет)? Дайте ответ цифрой:',
                              reply_markup=cancel)


async def set_child(message: types.Message, state: FSMContext):
    farm = CheckingFarm(value=message.text, message=message)
    if await farm.check_number():
        async with state.proxy() as data:
            data['child_number'] = farm.value
        await FarmsteadSearch.rooms_number.set()
        await message.answer('Какое количество номеров вам необходимо для ' +
                             'вашей компании? Дайте ответ цифрой:', reply_markup=cancel)


async def set_number(message: types.Message, state: FSMContext):
    farm = CheckingFarm(value=message.text, message=message)
    if await farm.check_number():
        async with state.proxy() as data:
            data['rooms_number'] = farm.value
            if 'regions' in data:
                await FarmsteadSearch.budget.set()
                await message.answer('Какой у вас диапазон бюджета на сутки на одного человека? ' + 
                                     'Например: 50-100 BYN, до 50 BYN, от 100 BYN', reply_markup=cancel)
            else:
                await FarmsteadSearch.start_date.set()
                await message.answer('В какой период времени планируете отдых? Выберете день заезда:',
                                    reply_markup=await SimpleCalendar().start_calendar())


async def set_start_date(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy() as data:
            data['start_date'] = date.strftime("%d/%m/%Y")
            await FarmsteadSearch.finish_date.set()
            await callback_query.message.delete()
            await callback_query.message.answer(f"Ок, вы выбрали <b><i>{data['start_date']}" +
                                                "</i></b>\nВыберете день отъезда:",
                                                reply_markup=await SimpleCalendar().start_calendar(date=data['start_date']),
                                                parse_mode='html')


async def set_finish_date(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy() as data:
            data['finish_date'] = date.strftime("%d/%m/%Y")
            farm = CheckingFarm(start_date=data['start_date'],
                                finish_date=data['finish_date'],
                                callback=callback_query)
            if await farm.check_date():
                await callback_query.message.delete()
                if 'budget' in data:
                    box = Checkbox(callback_query, *search.criteria[0], **search.criteria[1])
                    await FarmsteadSearch.criteria.set()
                    await callback_query.message.answer('Для вас есть 200 предложений. Давайте конкретизируем поиск.\n' +
                                                        'Выберете важные критерии для отдыха?', reply_markup=await box.get_box())
                else:
                    await callback_query.message.answer(
                        f"📋 Вы выбрали дом/усадьба в <b><i>'{data['name'].capitalize()}'</i></b> " +
                        f"для <b><i>{data['adults_number']}</i></b> взрослых, " +
                        f"<b><i>{data['child_number']}</i></b> детей, " +
                        f"<b><i>{data['rooms_number']}</i></b> номер(ов) " +
                        f"<b><i>{data['start_date']}</i></b> - <b><i>{data['finish_date']}</i></b>.\n" +
                        f"Всё верно?", parse_mode='html', reply_markup=is_it_correct) 


async def press_yes(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == None:
        await callback.answer()
        return
    await callback.answer()
    async with state.proxy() as data:
        await db.add_purchase(data)
        await callback.message.answer(f"✅ Мы отправили ваши данные хозяину '{data['name'].capitalize()}' " +
                                      f"для подтверждения свободных мест по вашему запросу.\nОжидайте ответа./start")
    await state.finish()


def register_handlers(dp: Dispatcher):

    dp.register_callback_query_handler(show_place, text='show_place')
    dp.register_message_handler(set_name, state=FarmsteadSearch.name)
    dp.register_message_handler(set_adult, state=FarmsteadSearch.adults_number)
    dp.register_message_handler(set_child, state=FarmsteadSearch.child_number)
    dp.register_message_handler(set_number, state=FarmsteadSearch.rooms_number)
    dp.register_callback_query_handler(set_start_date, simple_cal_callback.filter(),
                                       state=FarmsteadSearch.start_date) 
    dp.register_callback_query_handler(set_finish_date, simple_cal_callback.filter(),
                                       state=FarmsteadSearch.finish_date) 
    dp.register_callback_query_handler(press_yes, text='add_purchase',
                                       state=FarmsteadSearch.finish_date)
    dp.register_message_handler(search.set_budget, state=FarmsteadSearch.budget)
    dp.register_callback_query_handler(search.set_criteria, Checkbox.call_data.filter(), state=FarmsteadSearch.criteria)