from decouple import config

async def on_startup(dp):
    ADMIN_ID = config('ADMIN_ID')
    await dp.bot.send_message(chat_id=ADMIN_ID, text="Bot started")
    
if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp
    
    executor.start_polling(dp, on_startup=on_startup)