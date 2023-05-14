from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.files import JSONStorage

from decouple import config

API_TOKEN = config('TELEGRAM_API_KEY')

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = JSONStorage('STAGE.json')
dp = Dispatcher(bot, storage=storage)