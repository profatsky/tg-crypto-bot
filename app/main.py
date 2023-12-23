from aiogram.utils import executor

from loader import dp, bot
from config import ADMIN_ID
import handlers


async def on_startup(dp):
    print("Бот запущен")
    await bot.send_message(ADMIN_ID, "Я запущен!")

if __name__ == "__main__":
    handlers.register_handlers_users(dp)
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
