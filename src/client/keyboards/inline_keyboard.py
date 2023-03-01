from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from mysql_db.mysql_db import BaseWorking as db
from aiogram import types
from aiogram.utils.callback_data import CallbackData
from aiogram.types.input_media import InputMediaPhoto


async def get_start(login, user_id):
    start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    if await db.check_client_state(login, user_id):
        start_keyboard.add(
            KeyboardButton(text='Выход'),
            KeyboardButton(text='Личный кабинет'),
            KeyboardButton(text='Обратная связь')
        )
    else:
        start_keyboard.add(
            KeyboardButton(text='Вход'),
            KeyboardButton(text='Регистрация'),
            KeyboardButton(text='Обратная связь')
        )
    return start_keyboard



start_keyboard = InlineKeyboardMarkup(row_width=3)
start_keyboard.add(
    InlineKeyboardButton(text='Знаю место', callback_data='show_place'),
    InlineKeyboardButton(text='Популярное', callback_data='show_popular'),
    InlineKeyboardButton(text='Поиск', callback_data='show_search')
)

cancel = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text='Отмена', callback_data='cancel')
)

is_it_correct = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Да', callback_data='add_purchase'),
        InlineKeyboardButton(text='Нет', callback_data='cancel')
    ]
])


# Многофункциональный слайдер

class FarmSlider:

    def __init__(self,
                 cd_slider: CallbackData = {},
                 page: int = 0,
                 farm_list: list = [],
                 callback: types.CallbackQuery = None,
                 callback_data: dict = None,) -> None:
        
        self.__farm_list = farm_list
        self.__page = page
        self.__callback = callback
        self.__callback_data = callback_data
        self.__cd_slider = cd_slider

    async def __get_pathes(self):
        photos_path = [i[0] for i in self.__farm_list]
        names = [i[1] for i in self.__farm_list]
        beds = [i[2] for i in self.__farm_list]
        return photos_path, names, beds

    async def get_slider(self):
        photos_path, names, beds = await self.__get_pathes()
        with open(photos_path[0], 'rb') as photo_file:
            await self.__callback.message.answer_photo(photo=photo_file,
                                                       caption=f'1. Усадьба: {names[0]}\nКоличество мест: {beds[0]}',
                                                       reply_markup=await self.start_slider())

    async def start_slider(self, page: int = None):

        if page != None:
            self.__page = page

        whole_path = self.__farm_list
        has_next_page = len(whole_path) > self.__page + 1
        farm_slider = InlineKeyboardMarkup(row_width=3)
        if self.__page != 0:    
            farm_slider.insert(InlineKeyboardButton(text='⬅️',
                                                    callback_data=self.__cd_slider.new(self.__page - 1,
                                                                                          self.__page)))
        else:
            farm_slider.insert(InlineKeyboardButton(text='⬅️',
                                                    callback_data=self.__cd_slider.new(len(whole_path) - 1,
                                                                                          self.__page))
            )
        farm_slider.insert(InlineKeyboardButton(text='Подробнее',
                                                callback_data=self.__cd_slider.new('detail',
                                                                                      self.__page))
        )
        if has_next_page:
            farm_slider.insert(InlineKeyboardButton(text='➡️',
                                                    callback_data=self.__cd_slider.new(self.__page + 1,
                                                                                          self.__page)))

        else:
            farm_slider.insert(InlineKeyboardButton(text='➡️',
                                                    callback_data=self.__cd_slider.new(0,
                                                                                          self.__page)))
        return farm_slider

    async def process_farm_slider(self):
        photos_path, names, beds = await self.__get_pathes()
        if self.__callback_data['action'] == 'None':
            await self.__callback.answer()
        elif self.__callback_data['action'] == 'detail':
            return True, (photos_path, names, beds, self.__callback_data['page'])
        else:
            page = int(self.__callback_data.get('action'))
            with open(photos_path[page], 'rb') as photo_file:
                photo = InputMediaPhoto(media=photo_file, caption=f'{page + 1}. Усадьба: {names[page]}\nКоличество мест: {beds[page]}')
                await self.__callback.message.edit_media(media=photo, reply_markup=await self.start_slider(page=page))
        return False, None


# Перед заказом

async def order_or_holder(farm_name):
    order_or_holder = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Сделать заказ', callback_data=f'make_order:{farm_name}'),
                InlineKeyboardButton(text='Написать владельцу', callback_data='write_to_holder')
            ]
        ]
    )
    return order_or_holder


# Многофункциональный чекбокс

class Checkbox:
    
    """
    Universal checkbox, accepts names of fields as arguments.
    Returns a list of values marked '☑️'.
    """

    call_data = CallbackData('checkbox', 'action', sep='~')
    
    def __init__(self, callback: types.CallbackQuery, data: CallbackData = None, *args, **kwargs):
        self.__callback = callback
        self.__args = args
        self.__data = data
        self.__kwargs = kwargs

    async def get_box(self) -> InlineKeyboardMarkup:
        try:
            temp_table = await db.get_box_table(self.__callback.from_user.id, *self.__args)
            box_board = InlineKeyboardMarkup(row_width=2)
            for item in temp_table:
                box_board.insert(
                    InlineKeyboardButton(text=f'{item[1]} {item[2]}', callback_data=self.call_data.new(f'choose_{item[0]}'))
                )
            if self.__kwargs != {}:
                for k, v in self.__kwargs.items():
                    box_board.add(InlineKeyboardButton(text=f'{k}', callback_data=self.call_data.new(f'{v}')))
            box_board.add(
                InlineKeyboardButton(
                    text='Готово', callback_data=self.call_data.new('box_ready')
                )
            )
            return box_board
        except TypeError as e:
            try:
                await db.drop_checkbox(self.__callback.from_user.id)
            except:
                print("Checkbox wasn't created:", e)
                return

    async def process_box(self):
        await self.__callback.answer()
        res = []
        user_id = self.__callback.from_user.id

        for k, v in self.__kwargs.items():
            if self.__data['action'] == v:
                res = k
                await db.drop_checkbox(user_id)
        if self.__data['action'] == 'box_ready':
            if '☑️' not in [i[1] for i in await db.check_box(user_id)]:
                await self.__callback.message.edit_text(text= 'Вы ничего не выбрали!', reply_markup=await self.get_box())
                res = []
            else:
                box = await db.get_box_table(user_id)
                for i in box:
                    for j in i:
                        if j == '☑️':
                            res.append(i[2])
                await db.drop_checkbox(user_id)
                await self.__callback.message.delete()
        else:
            try:
                for item in self.__args:
                    if (await db.get_id_by_name(self.__data['action'], user_id))[0][0] == item:
                        await db.change_box(user_id, item)
                        await self.__callback.message.edit_reply_markup(reply_markup=await self.get_box())
            except:
                None
        if isinstance(res, str):
            res = res
        elif len(res) > 1:
            res = ', '.join(res)
        elif len(res) == 1:
            res = res[0]
        return res
    
    async def check_box(self):
        await db.drop_checkbox(self.__callback.from_user.id)


# Выбор дополнительных параметров и итоговый слайдер

after_criteria = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Посмотреть', callback_data='watch_choiсe'),
            InlineKeyboardButton(text='Добавить критерии', callback_data='add_criteria')
        ]
    ]
)