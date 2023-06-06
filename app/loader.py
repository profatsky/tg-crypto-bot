from aiogram import Bot
from aiogram.dispatcher import Dispatcher

from image_generator import ImageGenerator
from exchange_requests import ExchangeRequests
from config import TOKEN


bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
image_generator = ImageGenerator()
exchange_requests = ExchangeRequests()
