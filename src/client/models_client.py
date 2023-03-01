from aiogram.dispatcher.filters.state import State, StatesGroup
from mysql_db.mysql_db import BaseWorking as db
from aiogram import types
from keyboards import cancel


class FarmsteadSearch(StatesGroup):

    name = State()
    adults_number = State()
    child_number = State()
    rooms_number = State()
    start_date = State()
    finish_date = State()
    regions = State()
    budget = State()
    criteria = State()
    more_criteria = State()


class CheckingFarm:

    def __init__(self, name:str='', value: int=None, start_date: int=None, finish_date=None, message: types.Message=None, callback: types.CallbackQuery=None):
        
        self.__message = message
        self.__callback = callback
        self.__name = name
        self.__value = value
        self.__start_date = start_date
        self.__finish_date = finish_date


    async def check_name(self):
        if len(self.__name) > 255:
            await self.__message.answer('Слишком длинное название. Попробуйте ещё раз:', reply_markup=cancel)
        elif not db.check_farm_name(self.__name):
            await self.__message.answer('Такой агроусадьбы нет в базе. Попробуйте ещё раз:', reply_markup=cancel)
        else:
            return True

    
    async def check_number(self):
        if self.__value.isdigit() and 0 <= int(self.__value) < 127:
            return True
        else:
            await self.__message.answer('Введён неправильный формат.\nПопробуйте снова:', reply_markup=cancel)


    async def check_date(self):
        d1 = self.__start_date.split('/')
        d2 = self.__finish_date.split('/')
        if d2[::-1] > d1[::-1]:
            return True
        else:
            await self.__callback.answer('Нельзя установить дату отъезда раньше даты заезда')
    
    
    @property
    def name(self):
        return self.__name


    @property
    def value(self):
        return self.__value


    @property
    def date(self):
        return self.__start_date


    @property
    def date(self):
        return self.__finish_date


class ClientRegistration(StatesGroup):
    
    client_login = State()
    client_password = State()
    client_confirm_password = State()

    def __init__(self, login = None, password = None, confirm_password = None, message: types.Message = None):
        self.__login = login
        self.__password = password
        self.__confirm_password = confirm_password
        self.__message = message


    async def check_login(self):
        if await db.check_client_login(self.__login):
            return True
        else:
            await self.__message.answer('Такой логин уже существует. Придумайте новый.', reply_markup=cancel)

    
    async def check_password(self):
        if len(self.__password) < 224:
            return True
        else:
            await self.__message.answer('Слишком длинный пароль Не более 224 символов.', reply_markup=cancel)


    async def check_confirm_password(self):
        if self.__confirm_password == self.__password:
            return True
        else:
            await self.__message.answer('Пароли не совпадают. Попробуйте ещё раз', reply_markup=cancel)



    @property
    def login(self):
        return self.__login

    
    @property
    def password(self):
        return self.__password


    @property
    def confirm_password(self):
        return self.__confirm_password


class ClientLogin(StatesGroup):

    client_login = State()
    client_password = State()

    def __init__(self, login=None, password=None, message: types.Message=None):
        self.__login = login
        self.__password = password
        self.__message = message

    async def check_login(self):
        if await db.check_client_login(self.__login):
            await self.__message.answer("Такой логин не существует. Попробуйте ещё раз:", reply_markup=cancel)
        else:
            return True

    async def check_password(self):
        if await db.check_client_password(self.__login, self.__password):
            return True
        else:
            await self.__message.answer("Неправильный пароль. Попробуйте ещё раз:", reply_markup=cancel)

    @property
    def get_login(self):
        return self.__login
    
    @property
    def get_password(self):
        return self.__password


class ClientName:

    client_name: str = None

    def __init__(self, message: types.Message=None):
        self.__message = message

    async def check_name(self):
        res = await db.find_client_id(self.__message.from_user.id)
        if res[0]:
            return res[1]
        else:
            return self.__message.from_user.full_name