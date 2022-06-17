from aiogram.utils import executor

from loader import dp, bot
from config import admin_id
from handlers import rate


async def on_startup(dp):
    print("Бот запущен")
    await bot.send_message(admin_id, "Я запущен!")

rate.register_handlers_users(dp)

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
