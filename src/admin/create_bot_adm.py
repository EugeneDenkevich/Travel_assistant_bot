from aiogram.dispatcher import Dispatcher
from aiogram import Bot
import config_adm as conf
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()
bot_adm = Bot(token=conf.TOKEN)
dp_adm = Dispatcher(bot_adm, storage=storage)