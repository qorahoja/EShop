import os
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from data import Database
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
# States class definition
class Form(StatesGroup):
    waiting_name_for_reg = State()
    waiting_pass_for_reg = State()
    waiting_pass_for_log = State()




def create_database():
    db = Database("data.db")
    db.create_tables()
    db.close_connection()


def check_current_directory():
    current_directory = os.getcwd()
    if not any(entry.name == 'data.db' for entry in os.scandir(current_directory)):
        create_database()


def user_check(database, column_name, table_name):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    query = f"SELECT {table_name} FROM {column_name}"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]






# Initialize bot and dispatcher
bot = Bot(token="6595205342:AAFWRT5j0_7deBqRgjF2fZIQilDsdpFGji8")
dp = Dispatcher(bot, storage=MemoryStorage())

user_data = {}

# Define a command handler
@dp.message_handler(Command("start"), state="*")
async def start(message: types.Message, state: FSMContext):
    await message.reply("👋 Hello\n\nI'm EShop bot online magazine")

    user_ids = user_check('data.db', "users", "uid")

    if message.from_user.id not in user_ids:
        await message.answer("Hmm... I couldn't find you in my database. Let's do the registration\n Please enter your name")
        await state.set_state(Form.waiting_name_for_reg)
    else:
        await message.answer(f"{message.from_user.full_name}, please enter your password")
        await Form.waiting_pass_for_log.set()



@dp.message_handler(state=Form.waiting_name_for_reg)
async def reg_name(message: types.Message, state: FSMContext):
    
    user_data['name'] = message.text 


    await message.answer(f"{message.text}, please enter your password for the next step")
    await Form.waiting_pass_for_reg.set()


@dp.message_handler(state=Form.waiting_pass_for_reg)
async def reg_pass(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    name = user_data["name"]
    password = user_data['pass'] = message.text

    if message.text:

        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        query = "INSERT INTO users (uid, username, password) VALUES (?, ?, ?)"
        values = (user_id, name, password)

        cursor.execute(query, values)

        conn.commit()
        conn.close()





        await message.answer("Registration successful!")
        await state.finish()


@dp.message_handler(state=Form.waiting_pass_for_log)
async def pass_log(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    password_entered = message.text

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    query = "SELECT username, password FROM users WHERE uid = ?"
    cursor.execute(query, (user_id,))
    row = cursor.fetchone()  # Fetch only one row as we filter by user ID
    conn.close()

    if row and password_entered == row[1]:
        buttons = [[KeyboardButton(text="Catalog📔"), KeyboardButton(text="My Wallet👝")]]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
        await message.answer(f"Welcome {row[0]} What are you going to buy today?", reply_markup=keyboard)

        await state.finish()
    else:
        await message.answer("Invalid password")


@dp.message_handler(lambda message: message.text == "Catalog📔", state="*")
async def Catalog(message: types.Message):
    buttons = [[KeyboardButton(text="Toys"), KeyboardButton(text="Foods"), KeyboardButton(text="Phones")]]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
    await message.answer("Choose one of the catalog types", reply_markup=keyboard)





if __name__ == "__main__":
    check_current_directory()
    executor.start_polling(dp, skip_updates=True)
