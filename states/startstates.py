from aiogram.dispatcher.filters.state import StatesGroup, State


class ReviewState(StatesGroup):
    name = State()
    phone = State()
    text = State()
    rating = State()
    
    