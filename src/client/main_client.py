import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from aiogram.utils import executor
from create_bot import dp
import traceback
from handlers import start
from mysql_db.mysql_db import StartConnection, BaseWorking as db


async def bot_start(_):
    print("\n--- Client's bot has started ---")
    try:
        StartConnection.mysql_start()
        await db.clear_db()
        print("--- Data base has connected ---\n")
    except Exception:
        print("--- Data base has not connected for some reason ---\n\n", traceback.format_exc())


if __name__ == "__main__":

    start.register_handlers_client(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=bot_start)