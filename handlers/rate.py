import datetime
import requests
from typing import List
from re import match

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import CommandStart

from image_app import create_img


async def start(message: Message):
    await message.answer(
        "📉<b>Изменения стоимости криптовалюты</b>\n\n"
        "Введите команду и список криптовалют через запятую\n"
         "▹ /d (/day) - изменение цены за день\n"
         "▹ /w (/week) - изменение цены за неделю\n"
         "▹ /m (/month) - изменение цены за месяц"
    )


async def search(coins: list, days: int) -> List[dict]:
    coins_data = []
    for coin in coins:
        # Получаем id, токен, имя и изображение монеты
        coin_info = requests.get(
            f"https://api.coingecko.com/api/v3/search",
            params={"query": coin}
        ).json()
        if coin_info['coins']:
            coins_data.append(coin_info['coins'][0])

    if coins_data:
        # Получаем цену монеты
        params = {
            "ids": ",".join([coin['id'] for coin in coins_data]),
            "vs_currencies": "usd"
        }
        coins_price = requests.get(f"https://api.coingecko.com/api/v3/simple/price", params=params).json()
        # Соединяем данные о монете и о ее цене
        for count, coin in enumerate(coins_data):
            # Поиск цены в дату начала указанного интервала
            start_date = datetime.date.today() - datetime.timedelta(days=days)
            start_date = f"{start_date.day}-{start_date.month}-{start_date.year}"
            old_price = requests.get(
                f"https://api.coingecko.com/api/v3/coins/{coin['id']}/history?date={start_date}"
            ).json()
            old_price = old_price['market_data']['current_price']['usd']
            # Изменение цены за указанный период
            change = (coins_price[coin['id']]['usd'] - old_price) / (old_price / 100)
            # Сохранение необходимый данных
            coins_price[coin['id']].update({"change": change})
            coins_data[count].update(coins_price[coin['id']])
        return coins_data


async def main_func(message: Message, days: int = 30):
    coins = message.text.replace(match(r"/\w+\b", message.text).group(0), "")[1:]  # убрать команду из сообщения
    if coins:
        coins = coins.split(", ")  # создание списка с монетами, перечисленными в сообщении
        if len(coins) > 5:
            await message.answer("❗ Можно указывать не более 5 монет за раз")
        else:
            coins_data = await search(coins, days=days)
            if coins_data:
                img = await create_img(coins_data, days=days)
                await message.answer_photo(photo=img)
            else:
                await message.answer("❗ Некорректный ввод")
    else:
        await message.answer("❗ После команды нужно перечислить монеты через запятую! Например: /day bitcoin, ethereum")


async def day_rate(message: Message):
    await main_func(message, 1)


async def week_rate(message: Message):
    await main_func(message, 7)


async def month_rate(message: Message):
    await main_func(message, 31)


def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(start, CommandStart())
    dp.register_message_handler(day_rate, commands=["d", "day"])
    dp.register_message_handler(week_rate, commands=["w", "week"])
    dp.register_message_handler(month_rate, commands=["m", "month"])
