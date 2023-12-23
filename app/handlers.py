from re import match

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import CommandStart

from utils import run_func_in_process
from loader import exchange_requests, image_generator


async def start(message: Message):
    await message.answer(
        "📉<b>Изменения стоимости криптовалюты</b>\n\n"
        "Введите команду и список криптовалют через запятую\n"
         "▹ /d (/day) - изменение цены за день\n"
         "▹ /w (/week) - изменение цены за неделю\n"
         "▹ /m (/month) - изменение цены за месяц"
    )


async def send_coins_info(message: Message, days: int = 30):
    coins = message.text.replace(match(r"/\w+\b", message.text).group(0), "")[1:]
    if not coins:
        return await message.answer(
            "❗ После команды нужно перечислить монеты через запятую! "
            "Например: /day bitcoin, ethereum"
        )

    coins = coins.split(", ")
    if len(coins) > 5:
        return await message.answer("❗ Можно указывать не более 5 монет за раз")

    coins_data = await exchange_requests.get_coins_info(coins, days=days)
    if not coins_data:
        return await message.answer("❗ Некорректный ввод")

    img = await run_func_in_process(
        image_generator.create_image_with_cryptocurrency_rate,
        coins_data,
        days
    )
    await message.answer_photo(photo=img)


async def get_day_rate(message: Message):
    await send_coins_info(message, 1)


async def get_week_rate(message: Message):
    await send_coins_info(message, 7)


async def get_month_rate(message: Message):
    await send_coins_info(message, 31)


def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(start, CommandStart())
    dp.register_message_handler(get_day_rate, commands=["d", "day"])
    dp.register_message_handler(get_week_rate, commands=["w", "week"])
    dp.register_message_handler(get_month_rate, commands=["m", "month"])
