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
    waiting_pass_admin = State()
    waiting_for_catalog_name = State()
    selected_catalog = State()
    product_name = State()
    product_descriptoin = State()
    product_price = State()
    product_photo = State()
    user_select_catalog = State()
    user_select_product = State()





def create_database():
    db = Database("data.db")
    db.create_tables()
    db.close_connection()




def user_check(database, column_name, table_name):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    query = f"SELECT {table_name} FROM {column_name}"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]

def admin_check(database, column_name, table_name):
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
product = {}
user_product = {}

# Define a command handler
@dp.message_handler(Command("start"), state="*")
async def start(message: types.Message, state: FSMContext):
    await message.reply("👋")

    user_ids = user_check('data.db', "users", "uid")

    if message.from_user.id not in user_ids:
        await message.answer("Hmm... I couldn't find you in my database. Let's do the registration\n Please enter your name")
        await state.set_state(Form.waiting_name_for_reg)
    else:
        await message.answer(f"{message.from_user.full_name}, please enter your password")
        await Form.waiting_pass_for_log.set()


@dp.message_handler(Command("admin"), state="*")
async def admin(message: types.Message, state: FSMContext):

    user_ids = admin_check('data.db', "admins", "aid")

    if message.from_user.id not in user_ids:
        await message.answer("You are not a Admin so get out!!")
        await state.finish()
    else:
        await message.answer("Dear admin, please enter your password")
        await Form.waiting_pass_admin.set()



@dp.message_handler(state=Form.waiting_pass_admin)
async def admin_pass_check(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    password = message.text

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    query = "SELECT username, password FROM admins WHERE aid = ?"
    cursor.execute(query, (user_id,))
    row = cursor.fetchone()  # Fetch only one row as we filter by user ID
    conn.close()
    
    
    if row and password == row[1]:
        buttons = [[KeyboardButton(text="Statistics📊"), KeyboardButton(text="Settings⚙"), KeyboardButton(text="Add Catalog➕"), KeyboardButton(text="Add product to catalog➕")]]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
        await message.answer(f"Welcome {row[0]}! What will we do today?", reply_markup=keyboard)
        await state.finish()

    else:
        await message.answer("Invalit password please try again!")
        print(row[1], password)





@dp.message_handler(lambda message: message.text == "Statistics📊")
async def statistic(message: types.Message):
    await message.answer("It works")

@dp.message_handler(lambda message: message.text == "Settings⚙")
async def statistic(message: types.Message):
    await message.answer("It works")

@dp.message_handler(lambda message: message.text == "Add Catalog➕")
async def statistic(message: types.Message):
    remove_buttons = ReplyKeyboardRemove()
    await message.answer("Ok. Please enter catalog name", reply_markup=remove_buttons)
    await Form.waiting_for_catalog_name.set()


@dp.message_handler(lambda message: message.text == "Add product to catalog➕")
async def select_catalog(message: types.Message, state: FSMContext):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    query = "SELECT catalog_name FROM catalog"
    cursor.execute(query)
    rows = cursor.fetchall()  # Fetch all rows

    # Close the database connection
    conn.close()

    if rows:
        buttons = []
        for row in rows:
            buttons.append([KeyboardButton(text=row[0])])  # Each row contains one catalog name

        # Create a ReplyKeyboardMarkup with the dynamic buttons
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

        # Send a message with the dynamic buttons
        await message.answer("Please select a catalog:", reply_markup=keyboard)
        await Form.selected_catalog.set()

    else:
        await message.answer("No catalogs found.")



@dp.message_handler(state=Form.selected_catalog)
async def add_product(message: types.Message, state: FSMContext):
    product['catalog_name'] = message.text

    await message.answer("Please enter product name")
    await Form.product_name.set()


@dp.message_handler(state=Form.product_name)
async def take_product_name(message: types.Message, state: FSMContext):
    remove = ReplyKeyboardRemove()
    product["product_name"] = message.text

    await message.answer("Please enter product description", reply_markup=remove)
    await Form.product_descriptoin.set()


@dp.message_handler(state=Form.product_descriptoin)
async def take_product_descriptoin(message: types.Message, state: FSMContext):
    product["product_description"] = message.text

    await message.answer("Please enter product price")
    await Form.product_price.set()


@dp.message_handler(state=Form.product_price)
async def take_product_price(message: types.Message, state: FSMContext):
    product['product_price'] = message.text

    await message.answer("Last step. Please send Product photo")
    await Form.product_photo.set()


@dp.message_handler(content_types=types.ContentType.PHOTO, state=Form.product_photo)
async def take_product_photo(message: types.Message):
    photo_id = message.photo[-1].file_id
    catalog = product["catalog_name"]
    product_name = product["product_name"]
    product_description = product["product_description"]
    product_price = product["product_price"]

    # Ensure the directory exists
    os.makedirs('img', exist_ok=True)

    # Download the photo
    file = await bot.get_file(photo_id)
    photo_file = await bot.download_file_by_id(photo_id)

    # Save the photo to the IMG_DIR directory
    photo_file_path = os.path.join('img', f"{product_name}.jpg")
    with open(photo_file_path, 'wb') as new_file:
        new_file.write(photo_file.read())

    # Insert the product into the database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Retrieve the max product_id
    cursor.execute("SELECT MAX(product_id) FROM products")
    last_product_id = cursor.fetchone()[0]

    # Increment the product_id
    new_product_id = last_product_id + 1 if last_product_id else 1

    # Insert the product into the database
    query = "INSERT INTO products (product_id, product_catalog, product_name, product_description, product_price) VALUES (?, ?, ?, ?, ?)"
    values = (new_product_id, catalog, product_name, product_description, product_price)
    cursor.execute(query, values)
    conn.commit()
    conn.close()

    await message.reply("Product saved to database")
    




    







@dp.message_handler(state=Form.waiting_for_catalog_name)
async def catalog_name(message: types.Message, state: FSMContext):
    catalog = message.text
    
    # Connect to the database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Retrieve the last catalog_id
    cursor.execute("SELECT MAX(catalog_id) FROM catalog")
    last_catalog_id = cursor.fetchone()[0]

    # Increment the catalog_id
    new_catalog_id = last_catalog_id + 1 if last_catalog_id else 1

    # Insert the new catalog into the database
    query = "INSERT INTO catalog (catalog_id, catalog_name) VALUES (?, ?)"
    values = (new_catalog_id, catalog)
    cursor.execute(query, values)

    # Commit changes and close connection
    conn.commit()
    conn.close()

    buttons = [[KeyboardButton(text="Statistics📊"), KeyboardButton(text="Settings⚙"), KeyboardButton(text="Add Catalog➕"), KeyboardButton(text="Add product to catalog➕")]]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    await message.answer(f"Ok catalog created. Catalog name {catalog}", reply_markup=keyboard)
    await state.finish()



#USER SECTION






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





        
        buttons = [[KeyboardButton(text="Catalog📔"), KeyboardButton(text="My Wallet💰"), KeyboardButton(text="Basket 🛒")]]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
        await message.answer("Registration successful!", reply_markup=keyboard)
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
        buttons = [[KeyboardButton(text="Catalog📔"), KeyboardButton(text="My Wallet💰"), KeyboardButton(text="Basket 🛒")]]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
        await message.answer(f"Welcome {row[0]} What are you going to buy today?", reply_markup=keyboard)

        await state.finish()
    else:
        await message.answer("Invalid password")


@dp.message_handler(lambda message: message.text == "Catalog📔", state="*")
async def show_catalogs(message: types.Message, state: FSMContext):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    query = "SELECT catalog_name FROM catalog"
    cursor.execute(query)
    rows = cursor.fetchall()  # Fetch all rows

    # Close the database connection
    conn.close()

    if rows:
        buttons = []
        for row in rows:
            buttons.append([KeyboardButton(text=row[0])])  # Each row contains one catalog name

        # Create a ReplyKeyboardMarkup with the dynamic buttons
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

        # Send a message with the dynamic buttons
        await message.answer("Please select a catalog:", reply_markup=keyboard)
        await Form.user_select_catalog.set()

    else:
        await message.answer("No catalogs found.")

        await state.finish()



@dp.message_handler(lambda message: message.text == "Basket 🛒")
async def basket(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    query = "SELECT order_name, order_price FROM orders WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    row = cursor.fetchall()  # Fetch only one row as we filter by user ID


    for rows in row:
        print(row)
        caption = f'''
            Name: {rows[0]}\n\nPrice: {rows[1]}
        '''
        img_name = f"img/{rows[0]}.jpg"

        with open(img_name, 'rb') as photo:
                        # Create inline keyboard
            keyboard = types.InlineKeyboardMarkup()
            # Add a button to the keyboard
            button_text = f"Buy now"
            button_callback_data = f"buy_{rows[0]}"
            keyboard.add(types.InlineKeyboardButton(text=button_text, callback_data=button_callback_data))


            sent_photo = await bot.send_photo(chat_id=user_id, photo=photo, caption=caption, reply_markup=keyboard)
            # Store the caption along with the message ID for later retrieval
            await state.update_data({sent_photo.message_id: caption})
  


@dp.callback_query_handler(lambda c: c.data.startswith('buy_'))
async def inline_button_pressed(callback_query: types.CallbackQuery):
    print("Buy callBack")

    button_data = callback_query.data
    name = button_data.replace("buy_", "")
    print(name)
    
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    # Extract user_idds from callback_query
    user_id = callback_query.from_user.id
    
    # Define the SQL queries
    wallet_query = "SELECT how_much FROM wallet WHERE user_id = ?"
    price_query = "SELECT product_price FROM products WHERE product_name = ?"
    
    # Execute SQL queries and fetch results
    cursor.execute(wallet_query, (user_id,))
    wallet_row = cursor.fetchone()  # Assuming each user has a unique entry
    
    cursor.execute(price_query, (name,))
    price_row = cursor.fetchone()
    print(price_row)
    
    # Check if wallet amount is sufficient for the purchase
    if wallet_row is not None and price_row is not None:
        wallet_amount = int(wallet_row[0])
        product_price = int(price_row[0])
        
        print("Wallet Amount:", wallet_amount)
        print("Product Price:", product_price)
        
        if wallet_amount == product_price:
            # Update wallet (reduce amount by product price) and inform the user
            new_wallet_amount = wallet_amount - product_price
            update_query = "UPDATE wallet SET how_much = ? WHERE user_id = ?"
            cursor.execute(update_query, (new_wallet_amount, user_id))
            delete_order = "DELETE FROM orders WHERE order_name = ?"
            cursor.execute(delete_order, (name,))
            conn.commit()
            
            await bot.send_message(user_id, 'Paid')  
        else:
            await bot.send_message(user_id, 'Insufficient funds')  
    else:
        await bot.send_message(user_id, 'Error in processing transaction')  

    # Close database connection
    conn.close()

 
        
@dp.message_handler(lambda message: message.text == "My Wallet💰")
async def my_wallet(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    # Define the SQL query with a WHERE clause to filter rows by product_catalog
    query = "SELECT how_much FROM wallet WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()

    for row in rows:
        print(row[0])
        await message.answer(f"In your account has {row[0]}$")
    print(rows)



            





@dp.message_handler(state=Form.user_select_catalog)
async def user_select_catalog(message: types.Message, state: FSMContext):
    user_product["user_id"] = message.from_user.id
    user_id = message.from_user.id
    user_product["catalog"] = message.text

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    # Define the SQL query with a WHERE clause to filter rows by product_catalog
    query = "SELECT product_name, product_description, product_price FROM products WHERE product_catalog = ?"
    cursor.execute(query, (message.text,))
    rows = cursor.fetchall()

    # Process the retrieved rows
    for row in rows:
        print(rows)
        caption = f'''
            Name: {row[0]}\n\nDescription: {row[1]}\n\nPrice: {row[2]}
        '''
        img_name = f"img/{row[0]}.jpg"

        with open(img_name, 'rb') as photo:
            # Create inline keyboard
            keyboard = types.InlineKeyboardMarkup()
            # Add a button to the keyboard
            button_text = f"To Basket 🛒"
            button_callback_data = f"to_{row[0]}"
            keyboard.add(types.InlineKeyboardButton(text=button_text, callback_data=button_callback_data))

            # Send photo with caption and inline keyboard
            sent_photo = await bot.send_photo(chat_id=user_id, photo=photo, caption=caption, reply_markup=keyboard)
            # Store the caption along with the message ID for later retrieval
            await state.update_data({sent_photo.message_id: caption})

    # Close the database connection
    conn.close()
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith('to_'))
async def inline_button_pressed(callback_query: types.CallbackQuery):
    print("Order callback")
    user_id = user_product["user_id"]
    # Retrieve the data associated with the pressed inline button
    button_data = callback_query.data

    # Remove the "to_" prefix from the button data
    name = button_data.replace("to_", "")

    # Retrieve the catalog from the user_product dictionary (assuming user_product is defined elsewhere)
    catalog = user_product.get("catalog")

    if catalog:
        # Connect to the database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        # Define the SQL query with a WHERE clause to filter rows by product_catalog and product_name
        query = "SELECT product_name, product_description, product_price FROM products WHERE product_catalog = ? AND product_name = ?"
        cursor.execute(query, (catalog, name))
        rows = cursor.fetchall()

        for row in rows:
            print(row)
            # Define the SQL query with a WHERE clause to filter rows by product_catalog and product_name
            query = "INSERT INTO orders (user_id, order_name, order_description, order_price) VALUES (?, ?, ?, ?)"
            values = (user_id, row[0], row[1], row[2])
            cursor.execute(query, values)
            conn.commit()
            conn.close()

            await bot.send_message(user_id, "Product saved to basket")
            
        if not rows:  # If no rows were found
            await bot.send_message(callback_query.from_user.id, "Product not found.")
    else:
        await bot.send_message(callback_query.from_user.id, "Catalog not specified.")








if __name__ == "__main__":
    create_database()

    executor.start_polling(dp, skip_updates=True)
