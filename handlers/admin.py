from aiogram import types 
from aiogram.dispatcher import FSMContext
#deep link
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils.deep_linking import decode_payload, get_start_link
from aiogram.dispatcher.filters.state import StatesGroup, State


import json

from loader import dp
from models import User, Place, Review
from states.startstates import ReviewState

from decouple import config

ADMIN_ID = config('ADMIN_ID')

main_markup = types.InlineKeyboardMarkup(row_width=2)
main_markup.add(types.InlineKeyboardButton(text="Додати заклад", callback_data="add_place"))


# CRUD - create, read, update, delete

class PlaceStates(StatesGroup):
    name = State()
    address = State()
    instagram = State()
    confirm = State()


#декоратор для адміністратора
def admin(func):
    async def wrapper(message: types.Message):
        if message.from_user.id == int(ADMIN_ID):
            await func(message)
        else:
            await message.answer(f"Ви не адміністратор")
    return wrapper



@dp.message_handler(commands=['admin'], user_id=ADMIN_ID)
async def admin(message: types.Message):
    await message.answer("Привіт, адміністраторе, що ти хочеш зробити?", reply_markup=main_markup)


@dp.callback_query_handler(text="add_place")
async def start_add_place(call: types.CallbackQuery):
    await call.message.edit_text("Введіть назву закладу")
    await PlaceStates.name.set()

@dp.message_handler(state=PlaceStates.name)
async def add_place_name(message: types.Message, state: FSMContext): 
    name = message.text
    await state.update_data(name=name)
    await message.answer("Введіть адресу закладу")
    await PlaceStates.next()

@dp.message_handler(state=PlaceStates.address)
async def add_place_address(message: types.Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer("Введіть посилання на Instagram закладу")
    await PlaceStates.next()
    
@dp.message_handler(state=PlaceStates.instagram)
async def add_place_instagram(message: types.Message, state: FSMContext):
    instagram = message.text
    await state.update_data(instagram=instagram)
    data = await state.get_data()
    text = f'Перевірте правильність введених даних: \nНазва: {data.get("name")}\nАдреса: {data.get("address")}\nInstagram: {data.get("instagram")}'
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="Так", callback_data="confirm"), types.InlineKeyboardButton(text="Ні", callback_data="cancel"))
    
    await message.answer(text, reply_markup=markup)
    await PlaceStates.next()
    
@dp.callback_query_handler(text="confirm", state=PlaceStates.confirm)
async def add_place_confirm(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    place = Place.create(name=data.get("name"), address=data.get("address"), instagram=data.get("instagram"))
    await call.message.answer("Заклад додано")
    link = await get_start_link(payload=json.dumps({"place_id" : place.id}) , encode=True)
    await call.message.answer(link)
    await state.finish()