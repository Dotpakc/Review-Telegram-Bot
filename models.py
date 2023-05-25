from peewee import *

# db = SqliteDatabase('data.db')
db = PostgresqlDatabase(
    database='Review-Telegram-Bot',
    user='postgres',
    password='1234',
    host='localhost',
    port='5432'
)

class BaseModel(Model): # Створюємо базовий клас моделі
    class Meta: # Вказуємо, що модель буде використовувати базу даних db
        database = db
        
class User(BaseModel): # Створюємо модель користувача        
    id = BigAutoField() # id користувача
    name = CharField() # Ім'я користувача
    phone = CharField() # Телефон користувача
    
# Модель для закладів
class Place(BaseModel):
    id = BigAutoField() # id закладу
    name = CharField() # Назва закладу
    address = CharField() # Адреса закладу
    instagram = CharField() # Instagram закладу
    
    
# Створюємо модель відгуку
class Review(BaseModel):
    id = BigAutoField() # id відгуку
    user_id = ForeignKeyField(User, backref='reviews') # Користувач, який залишив відгук
    place_id = ForeignKeyField(Place, backref='reviews') # Заклад, про який залишений відгук
    text = TextField() # Текст відгуку
    rating = IntegerField() # Оцінка відгуку
    date = DateTimeField() # Дата відгуку
    



def init_db(): # Функція для створення таблиць
    db.connect()
    db.create_tables([User, Place, Review])
    db.close()
    
if __name__ == '__main__':
    init_db()
    