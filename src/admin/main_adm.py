import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from create_bot_adm import bot_adm, dp_adm
from aiogram.utils import executor
from admin_farmstead import admin_farmstead_handlers
from adm_login import adm_login_handlers
from mysql_db.mysql_db import StartConnection
import traceback


async def holder_bot_start(_):
    print("\n--- Holder's bot has started ---")
    try:
        StartConnection.mysql_start()
        print("--- Data base has connected ---\n")
    except Exception:
        print("--- Data base has not connected for some reason ---\n\n", traceback.format_exc())


admin_farmstead_handlers.register_handlers_admin(dp_adm)
adm_login_handlers.register_handlers_admin_login(dp_adm)
executor.start_polling(dp_adm, skip_updates=True, on_startup=holder_bot_start)