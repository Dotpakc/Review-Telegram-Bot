from aiogram import types 
from aiogram.dispatcher import FSMContext
#deep link
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils.deep_linking import decode_payload, get_start_link

import json

from loader import dp
from models import User, Place, Review
from states.startstates import ReviewState


#TODO Кнопка пропустити 
skip_markup = types.InlineKeyboardMarkup()
skip_markup.add(types.InlineKeyboardButton(text="Пропустити", callback_data="skip"))


review_stars_markup = types.InlineKeyboardMarkup(row_width=1)
review_stars_markup.add(types.InlineKeyboardButton(text="⭐️", callback_data="1"),
                        types.InlineKeyboardButton(text="⭐️⭐️", callback_data="2"),
                        types.InlineKeyboardButton(text="⭐️⭐️⭐️", callback_data="3"),
                        types.InlineKeyboardButton(text="⭐️⭐️⭐️⭐️", callback_data="4"),
                        types.InlineKeyboardButton(text="⭐️⭐️⭐️⭐️⭐️", callback_data="5"),
                        types.InlineKeyboardButton(text="⭐️⭐️⭐️⭐️⭐️✨", callback_data="6"))





# TODO Додати в адмінку можливість додавати заклади та отримувати посилання на них
@dp.message_handler(commands=['link'])
async def get_link(message: types.Message):
    link = await get_start_link(payload=json.dumps({"place_id" : 1}) , encode=True)
    await message.answer(link)




#лінк відгуку
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    args = message.get_args()
    if args:
        payload = json.loads(decode_payload(args))
        place_id = payload.get('place_id')
        user = User.get_or_none(User.id == message.from_user.id)
        if not user:
            await message.answer("Привіт, хочу стобою познайомитись до того як ти залишеш відгук, як тебе звати?")
            await ReviewState.name.set()
        else:
            await message.asnwer("Привіт, рад тебе знову тут бачити, напиши свій відгук", reply_markup=skip_markup)
            await ReviewState.text.set()
        await state.update_data(place_id=place_id)
    else:
        await message.answer("Привіт, ти напевно хочеш залишити відгук про заклад. Будь ласка, скануй QR-код на столі")
        

@dp.message_handler(state=ReviewState.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer(f'Гарне ім\'я, {name}\n Тепер відправ мені свій номер телефону\n ⬇️Натисни кнопку на клавіатурі⬇️', 
                         reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton(
                                     text="Надіслати номер телефону", 
                                     request_contact=True)))
    await ReviewState.next()
    
@dp.message_handler(state=ReviewState.phone, content_types=types.ContentTypes.CONTACT)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    data = await state.get_data()
    User.create(id=message.from_user.id, name=data.get('name'), phone=data.get('phone'))
    await message.answer("Дякую, тепер напиши свій відгук", reply_markup=skip_markup)
    await ReviewState.next()

@dp.callback_query_handler(text="skip", state=ReviewState.text)
async def skip_text(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('Добре, тоді постав оцінку за заклад', reply_markup=review_stars_markup)
    await ReviewState.next()

@dp.message_handler(state=ReviewState.text)
async def get_text(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)
    await message.answer("Дякую, тепер напиши свою оцінку за заклад", reply_markup=review_stars_markup)
    await ReviewState.next()
    
@dp.callback_query_handler(state=ReviewState.rating)
async def get_rating(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('Дякую, твій відгук збережено')
    data = await state.get_data()
    user = User.get_or_none(User.id == call.from_user.id)
    place = Place.get_or_none(Place.id == data.get('place_id'))
    Review.create(user_id=user, place_id=place, text=data.get('text'), rating=call.data)
    await state.finish()