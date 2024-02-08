import os
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from data import Database
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import random
import asyncio
import matplotlib.pyplot as plt

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
    new_password = State()
    wait_order = State()
    deliver_name = State()
    deliver_phone = State()
    deliver_car = State()
    deliver_reg_pass = State()
    deliver_log = State()
    deliver_busy = State()
    deliver_password = State()
    statistic_ = State()
    





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


import random

def generate_unique_numbers(num_of_numbers):
    # Generate a list of all possible 6-digit numbers
    all_numbers = [str(i).zfill(6) for i in range(1000000)]

    # Shuffle the list to get a random order
    random.shuffle(all_numbers)

    # Take the required number of unique random 6-digit numbers
    unique_numbers = random.sample(all_numbers, num_of_numbers)

    return unique_numbers








# Initialize bot and dispatcher
bot = Bot(token="6595205342:AAFWRT5j0_7deBqRgjF2fZIQilDsdpFGji8")
dp = Dispatcher(bot, storage=MemoryStorage())

user_data = {}
product = {}
user_product = {}
deliver_data = {}

deliver = False

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


@dp.message_handler(commands=['deliver'], state="*")
async def deliver_reg(message: types.Message, state: FSMContext):
    del_id = message.from_user.id

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    deliver_exists_query = "SELECT deliver_id FROM deliverables WHERE deliver_id = ?"
    cursor.execute(deliver_exists_query, (del_id,))
    row = cursor.fetchone()

    if row:
        # Deliverer already exists, prompt for password
        await message.answer("Hello Mr please enter your password")
        await Form.deliver_log.set()
    else:
        # New deliverer, prompt for name
        await message.answer("Hello new deliver, can you tell me your name")
        await Form.deliver_name.set()

    conn.close()


@dp.message_handler(commands=['deliver_on'])
async def deliver_on(message: types.Message):
    global deliver
    admin_ids = admin_check('data.db', "admins", "aid")

    if message.from_user.id not in admin_ids:
        await message.answer('You do not have permission to use this command')
    else:
        deliver = True
        await message.answer('Delivery service is now enabled')

@dp.message_handler(commands=['deliver_off'])
async def deliver_off(message: types.Message):
    global deliver
    admin_ids = admin_check('data.db', "admins", "aid")
    
    if not deliver:
        await message.answer("Delivery service is already disabled")
    elif message.from_user.id not in admin_ids:
        await message.answer('You do not have permission to use this command')
    else:
        deliver = False
        await message.answer('Delivery service is now disabled')



@dp.message_handler(state=Form.deliver_log)
async def check_del_pass(message: types.Message, state: FSMContext):
    password = message.text
    del_id = message.from_user.id
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    pasword = "SELECT deliver_pass, deliver_name FROM deliverables WHERE deliver_id = ?"

    cursor.execute(pasword, (del_id,))

    row = cursor.fetchall()


    for i in row:
        if password == i[0]:
            await message.answer(f"Welcome {i[1]}!")

            await state.finish()

        else:
            await message.answer("Incorrect password")




@dp.message_handler(state=Form.deliver_name)
async def deliver_name(message: types.Message, state: FSMContext):
    deliver_data["deliver_name"] = message.text

    await message.answer(f"Ok nice too meet you {message.text} Please enter your strong password")
    await Form.deliver_reg_pass.set()


@dp.message_handler(state=Form.deliver_reg_pass)
async def deliver_pass(message: types.Message, state: FSMContext):
    deliver_data['deliver_pass'] = message.text
    await message.answer(f"Ok and then enter your car name like Matiz e.x")

    await Form.deliver_car.set()
 

@dp.message_handler(state=Form.deliver_car)
async def deliver_car(message: types.Message, state: FSMContext):
    deliver_data["deliver_car"] = message.text
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("Share Contact", request_contact=True)
    keyboard.add(button)

    await message.answer("You have a very nice car. The last step can you give me your number please", reply_markup=keyboard)
    await state.finish()


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: types.Message):
    user_id = message.from_user.id
    contact = message.contact["phone_number"]
    
    deliver_n = deliver_data["deliver_name"]
    deliver_c = deliver_data["deliver_car"]
    deliver_p = deliver_data['deliver_pass']

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    add_delivry_data = "INSERT INTO deliverables (deliver_id, deliver_name, deliver_car, deliver_number, deliver_pass, deliver_status) VALUES (?, ?, ?, ?, ?, ?)"
    values = (user_id, deliver_n, deliver_c, contact, deliver_p, "empty")
    cursor.execute(add_delivry_data, values)

    conn.commit()
    conn.close()

    await message.answer("Thank you new deliver i save all information about you if new order registred i will tell you")






    







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
        buttons = [[KeyboardButton(text="Statistics📊"), KeyboardButton(text="Settings⚙"), KeyboardButton(text="Add Catalog➕"), KeyboardButton(text="Add product to catalog➕"), KeyboardButton(text="Orders")]]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
        await message.answer("Welcome Admin!", reply_markup=keyboard)
        await state.finish()

    else:
        await message.answer("Invalit password please try again!")



@dp.message_handler(lambda message: message.text == "Orders")
async def admin_orders(message: types.Message, state: FSMContext):
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
            buttons.append([KeyboardButton(text=row[0])])

        # Add the "Return to top🔙" button after all the catalog buttons
        buttons.append([KeyboardButton(text="Return to top🔙")])

        # Create a ReplyKeyboardMarkup with the dynamic buttons
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

        # Send a message with the dynamic buttons
        await message.answer("Please select a catalog:", reply_markup=keyboard)
        await Form.wait_order.set()


@dp.message_handler(state=Form.wait_order)
async def catalog_order(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    catch_products = "SELECT product_name FROM products WHERE product_catalog = ?"

    cursor.execute(catch_products, (message.text,))
    products = cursor.fetchall()

    for row in products:
        print(row[0])
        catch_orders = "SELECT user_id, order_name, order_price, order_status FROM orders WHERE order_name = ?"

        cursor.execute(catch_orders, (row[0],))

        orders_row = cursor.fetchall()

        for row_order in orders_row:
            print(row_order[0])
            catch_user_name = "SELECT username FROM users WHERE uid = ?"

            cursor.execute(catch_user_name, (row_order[0],))
            row_names = cursor.fetchall()

            for names in row_names:
                caption = f'''
                Username: {names[0]}\n\nOrder Name: {row_order[1]}\n\nPrice: {row_order[2]}\n\n Order status: {row_order[3]}
                '''
                img_name = f"img/{row[0]}.jpg"
                with open(img_name, 'rb') as photo:


                    sent_photo = await bot.send_photo(chat_id=user_id, photo=photo, caption=caption)
                    
                    # Store the caption along with the message ID for later retrieval
                    await state.update_data({sent_photo.message_id: caption})

            button = [[KeyboardButton(text="Return to top🔙")]]
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)
        await bot.send_message(user_id, f"Orders for {message.text} catalog", reply_markup=keyboard)
                






from aiogram import types

@dp.message_handler(lambda message: message.text == "Statistics📊")
async def statistic(message: types.Message):
    button = [[KeyboardButton(text="Return to top🔙")]]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)

    if not os.path.exists('plots'):
        os.makedirs('plots')

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT order_name, order_status FROM orders")
    rows = cursor.fetchall()

    # Dictionary to store products by catalog for both paid and unpaid orders
    products_by_catalog_paid = {}
    products_by_catalog_unpaid = {}
    product_count_paid = 0
    product_count_unpaid = 0

    for row in rows:
        cursor.execute("SELECT product_catalog, product_name FROM products WHERE product_name = ?", (row[0],))
        products = cursor.fetchall()
        for product in products:
            catalog = product[0]
            product_name = product[1]
            if row[1] == "Paid":
                if catalog not in products_by_catalog_paid:
                    products_by_catalog_paid[catalog] = []
                products_by_catalog_paid[catalog].append(product_name)
                product_count_paid += 1
            elif row[1] == "Unpaid":
                if catalog not in products_by_catalog_unpaid:
                    products_by_catalog_unpaid[catalog] = []
                products_by_catalog_unpaid[catalog].append(product_name)
                product_count_unpaid += 1

    # Calculate percentages for paid products
    percentages_paid = [(len(products) / product_count_paid) * 100 for products in products_by_catalog_paid.values()]
    labels_paid = list(products_by_catalog_paid.keys())

    # Calculate percentages for unpaid products
    percentages_unpaid = [(len(products) / product_count_unpaid) * 100 for products in products_by_catalog_unpaid.values()]
    labels_unpaid = list(products_by_catalog_unpaid.keys())

    # Sending the message indicating the number of phones sold from each catalog for paid products
    paid_message = "Number of phones sold from each catalog for paid products:\n"
    for catalog, phones_sold in products_by_catalog_paid.items():
        paid_message += f"- {catalog}: {len(phones_sold)} phones\n"

    await message.answer(paid_message)

    # Plotting for paid products
    plt.figure(figsize=(12, 6))
    plt.pie(percentages_paid, labels=labels_paid, autopct='%1.1f%%', startangle=140)
    plt.title('Percentage of Paid Products by Catalog')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the plot to the plots directory
    plt.savefig('plots/paid.png')

    # Sending the paid plot as a photo with caption
    with open('plots/paid.png', 'rb') as photo:
        await message.reply_photo(photo, caption="Percentage of Paid Products by Catalog")

    # Sending the message indicating the number of phones sold from each catalog for unpaid products
    unpaid_message = "Number of phones sold from each catalog for unpaid products:\n"
    for catalog, phones_sold in products_by_catalog_unpaid.items():
        unpaid_message += f"- {catalog}: {len(phones_sold)} phones\n"

    await message.answer(unpaid_message)

    # Plotting for unpaid products
    plt.figure(figsize=(12, 6))
    plt.pie(percentages_unpaid, labels=labels_unpaid, autopct='%1.1f%%', startangle=140)
    plt.title('Percentage of Unpaid Products by Catalog')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the plot to the plots directory
    plt.savefig('plots/unpaid.png')

    # Sending the unpaid plot as a photo with caption
    with open('plots/unpaid.png', 'rb') as photo:
        await message.reply_photo(photo, caption="Percentage of Unpaid Products by Catalog")






        


@dp.message_handler(lambda message: message.text == "Return to top🔙", state="*")
async def back(message: types.Message, state:FSMContext):
    print("top")
    id = message.from_user.id

    conn = sqlite3.connect("data.db")

    cursor = conn.cursor()

    admin_id = "SELECT aid FROM admins"


    cursor.execute(admin_id)
    admin_row = cursor.fetchall()

    print(admin_row)


    for admins in admin_row:
        print(admins[0])
        if admins[0] == id:

                    buttons = [[KeyboardButton(text="Statistics📊"), KeyboardButton(text="Settings⚙"), KeyboardButton(text="Add Catalog➕"), KeyboardButton(text="Add product to catalog➕")]]
                    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
                    await message.answer("You are back to the beginning", reply_markup=keyboard)

        else:
                buttons = [[KeyboardButton(text="Catalog📔"), KeyboardButton(text="My Wallet💰"), KeyboardButton(text="Basket 🛒"), KeyboardButton(text="Order history📋")]]
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
                await message.answer('You are back to the beginning', reply_markup=keyboard)


    


@dp.message_handler(lambda message: message.text == "Settings⚙")
async def statistic(message: types.Message):
    button = [[KeyboardButton(text="Return to top🔙"), KeyboardButton(text="Change Password🛂")]]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)
    await message.answer("Select the setting you want to adjust", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Change Password🛂")
async def ch_p(message: types.Message, state: FSMContext):
    
    await message.answer("Enter your new password")

    await Form.new_password.set()


@dp.message_handler(state=Form.new_password)
async def new_password(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()


        
        update_query = "UPDATE admins SET password = ? WHERE aid = ?"
        cursor.execute(update_query, (message.text, user_id,))
        conn.commit()
        buttons = [[KeyboardButton(text="Statistics📊"), KeyboardButton(text="Settings⚙"), KeyboardButton(text="Add Catalog➕"), KeyboardButton(text="Add product to catalog➕")]]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
        await message.answer(f'Your new password {message.text}', reply_markup=keyboard)
        
        await state.finish()



    

@dp.message_handler(lambda message: message.text == "Add Catalog➕")
async def statistic(message: types.Message):
 
    button = [[KeyboardButton(text="Return to top🔙")]]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)
    await message.answer("Ok. Please enter catalog name", reply_markup=keyboard)
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
            buttons.append([[KeyboardButton(text=row[0]), KeyboardButton(text="Return to top🔙")]])  # Each row contains one catalog name

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
    button = [[KeyboardButton(text="Return to top🔙")]]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)

    await message.answer("Please enter product name", reply_markup=keyboard)
    await Form.product_name.set()


@dp.message_handler(state=Form.product_name)
async def take_product_name(message: types.Message, state: FSMContext):
    button = [[KeyboardButton(text="Return to top🔙")]]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)
    product["product_name"] = message.text

    await message.answer("Please enter product description", reply_markup=keyboard)
    await Form.product_descriptoin.set()


@dp.message_handler(state=Form.product_descriptoin)
async def take_product_descriptoin(message: types.Message, state: FSMContext):
    product["product_description"] = message.text
    button = [[KeyboardButton(text="Return to top🔙")]]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)

    await message.answer("Please enter product price", reply_markup=keyboard)
    await Form.product_price.set()


@dp.message_handler(state=Form.product_price)
async def take_product_price(message: types.Message, state: FSMContext):
    product['product_price'] = message.text
    button = [[KeyboardButton(text="Return to top🔙")]]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)

    await message.answer("Last step. Please send Product photo", reply_markup=keyboard)
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
        open_wallet = "INSERT INTO wallet (user_id,how_much) VALUES (?, ?)"
        wallet_value = (user_id, 0)
        values = (user_id, name, password)

        cursor.execute(query, values)
        cursor.execute(open_wallet, wallet_value)

        conn.commit()
        conn.close()





        
        buttons = [[KeyboardButton(text="Catalog📔"), KeyboardButton(text="My Wallet💰"), KeyboardButton(text="Basket 🛒"), KeyboardButton(text="Order history📋")]]
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
        buttons = [[KeyboardButton(text="Catalog📔"), KeyboardButton(text="My Wallet💰"), KeyboardButton(text="Basket 🛒"), KeyboardButton(text="Order history📋")]]
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
            buttons.append([KeyboardButton(text=row[0])])

        # Add the "Return to top🔙" button after all the catalog buttons
        buttons.append([KeyboardButton(text="Return to top🔙")])

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
    query = "SELECT order_id, order_name, order_price FROM orders WHERE user_id = ? AND order_status = ?"
    cursor.execute(query, (user_id, "Unpaid",))
    row = cursor.fetchall()  # Fetch only one row as we filter by user ID


    for rows in row:
        global product_name
        print(rows)
        product_name = rows[1]
        if rows:
            caption = f'''
                Name: {rows[1]}\n\nPrice: {rows[2]}
            '''
            img_name = f"img/{rows[1]}.jpg"

            with open(img_name, 'rb') as photo:
                            # Create inline keyboard
                keyboard = types.InlineKeyboardMarkup()
                # Add a button to the keyboard
                button_text = f"Buy now"
                button_callback_data = f"buy_{rows[0]}"
                keyboard.add(types.InlineKeyboardButton(text=button_text, callback_data=button_callback_data))
                button = [[KeyboardButton(text="Return to top🔙")]]
                back = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)

                sent_photo = await bot.send_photo(chat_id=user_id, photo=photo, caption=caption, reply_markup=keyboard)
                
                # Store the caption along with the message ID for later retrieval
                await state.update_data({sent_photo.message_id: caption})
        else:
            button = [[KeyboardButton(text="Return to top🔙"), KeyboardButton(text="Catalog📔")]]
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)
            await message.answer("You have not added anything to your basket yet! If you want to buy something, go to the Catalog", reply_markup=keyboard)
    await bot.send_message(user_id, "Select the product you want to buy", reply_markup=back)


@dp.message_handler(lambda message: message.text == "Order history📋")
async def history(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    conn = sqlite3.connect("data.db")

    cursor = conn.cursor()

    archived_orders = "SELECT order_name, order_price, order_status FROM orders WHERE user_id = ? AND order_status = ?"

    row = cursor.execute(archived_orders, (user_id, "Paid"))

    for rows in row:
        if rows:
            caption = f'''
                📛Name: {rows[0]}\n\n💸Price: {rows[1]}\n\n🗽Status: {rows[2]}
            '''
            img_name = f"img/{rows[0]}.jpg"
            with open(img_name, 'rb') as photo:
                button = [[KeyboardButton(text="Return to top🔙"), KeyboardButton(text="Catalog📔")]]
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)
                sent_photo = await bot.send_photo(chat_id=user_id, photo=photo, caption=caption, reply_markup=keyboard)
                # Store the caption along with the message ID for later retrieval
                await state.update_data({sent_photo.message_id: caption})
        else:
            button = [[KeyboardButton(text="Return to top🔙"), KeyboardButton(text="Catalog📔")]]
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)
            await message.answer('You have not purchased a product yet! If you want to order, go to our Catalog', reply_markup=keyboard)
        


@dp.callback_query_handler(lambda c: c.data.startswith('buy_'))
async def inline_button_pressed(callback_query: types.CallbackQuery):


    button_data = callback_query.data
    global product_id
    product_id = button_data.replace("buy_", "")

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
    
    cursor.execute(price_query, (product_name,))
    price_row = cursor.fetchone()

    
    # Check if wallet amount is sufficient for the purchase
    if wallet_row is not None and price_row is not None:
        wallet_amount = int(wallet_row[0])
        product_price = int(price_row[0])

        if wallet_amount == product_price or wallet_amount >= product_price:
            # Update wallet (reduce amount by product price) and inform the user
            new_wallet_amount = wallet_amount - product_price
            
            update_query = "UPDATE wallet SET how_much = ? WHERE user_id = ?"
            
            cursor.execute(update_query, (new_wallet_amount, user_id))
            
            order_archiving = "UPDATE orders SET order_status = ? WHERE user_id = ? AND order_id = ?"

            order_id = "SELECT order_id FROM orders WHERE order_id = ?"
            cursor.execute(order_id, (product_id,))
            row = cursor.fetchall()

            for i in row:
                cursor.execute(order_archiving, ("Paid", user_id, i[0],))
            
            conn.commit()

            
            
            if deliver == True:
                button = [[KeyboardButton(text="Delivery🛫"), KeyboardButton(text="Take away🫴")]]
            
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)
                
                await bot.send_message(user_id, 'How do you want to receive your order?', reply_markup=keyboard) 
            else:
                cursor.execute("")
                await bot.send_message(user_id, "You can pick up your order")

        else:
            await bot.send_message(user_id, 'Insufficient funds')  
    else:
        await bot.send_message(user_id, 'Error in processing transaction')  

    # Close database connection
    conn.close()

 


@dp.message_handler(lambda message: message.text == "Delivery🛫")
async def delivery(message: types.Message, state: FSMContext):





        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        button = KeyboardButton("Share Location", request_location=True)
        keyboard.add(button)
        
        await message.answer("Please share your location", reply_markup=keyboard)

# Close the database connection when done

@dp.message_handler(content_types=types.ContentType.LOCATION)
async def handle_location(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    location = message.location

    # Connect to the database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Retrieve available deliveries
    cursor.execute("SELECT deliver_name, deliver_car, deliver_number, deliver_id FROM deliverables WHERE deliver_status = 'empty'")
    available_deliveries = cursor.fetchall()
    
    if available_deliveries:
        longitude = message.location.longitude
        latitute = message.location.latitude
        global deliver_id
        location = "INSERT INTO locations (user_id, deliver_id,order_id , longtude, latitute) VALUES (?, ?, ?, ?,?)"

        

 
        random_deliver = random.choice(available_deliveries)
        deliver_name, deliver_car, deliver_number, deliver_id = random_deliver

        cursor.execute("UPDATE deliverables SET deliver_status = 'busy', order_id = ?, order_name = ?, status = 'started' WHERE deliver_id = ?", (product_id, product_name ,deliver_id,))
        cursor.execute("UPDATE orders SET deliver_id = ?, order_status = 'Paid', delivry_status = 'deliver' WHERE user_id = ? AND order_id = ?", (deliver_id, user_id, product_id,))
        cursor.execute(location, (user_id, deliver_id, product_id, longitude, latitute,))
        conn.commit()

        await message.answer(f"The supplier is on the way\n\nName: {deliver_name}\n\nPhone Number: {deliver_number}\n\nCar: {deliver_car}")

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True) 
        button = KeyboardButton("I received the order")
        keyboard.add(button)

        await bot.send_message(deliver_id, f'You have a new order', reply_markup=keyboard)
    else:
        await message.answer("Sorry, all delivery agents are currently busy. Please wait for your turn.")
        while True:
                print('wait')
                await asyncio.sleep(30)   
                
                # Add a delay to avoid constant querying
                
                conn = sqlite3.connect('data.db')
                cursor = conn.cursor()

                

                print(f"Order_id {product_id}")

                cursor.execute("SELECT status FROM deliverables")
                delivery_status = cursor.fetchall()
                print(delivery_status)
                for i in delivery_status:
                    print(f'I {i[0]}')


                    if i and i[0] == 'finished':
                        print('Finish')
                        cursor.execute("SELECT delivry_status FROM orders WHERE order_id = ?", (product_id,))
                        delivery_order_status = cursor.fetchone()

                        if delivery_order_status and delivery_order_status[0] != 'delivery':
                            cursor.execute("UPDATE orders SET delivry_status = ? WHERE order_id = ?", ("delivery", product_id))
                            conn.commit()

                            cursor.execute("SELECT deliver_id FROM deliverables")
                            delivery_agent_id = cursor.fetchone()
                            print(delivery_agent_id)

                            if delivery_agent_id:
                            
                                button = [[KeyboardButton(text="I received the order")]]
                                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)
                                cursor.execute("UPDATE deliverables SET deliver_status = 'busy', order_id = ?, order_name = ?, status = 'started' WHERE deliver_id = ?", (product_id, product_name ,deliver_id,))
                                conn.commit()
                                await bot.send_message(delivery_agent_id[0], 'You have a new order', reply_markup=keyboard)

                                cursor.execute("SELECT deliver_id FROM deliverables WHERE order_id = ?", (product_id,))

                                rowss = cursor.fetchall()

                                for h in rowss:

                                
                                    cursor.execute("SELECT deliver_name, deliver_number, deliver_car, order_id FROM deliverables WHERE deliver_id = ?", (h[0],))
                                    row = cursor.fetchall()
                                    for i in row:
                                        cursor.execute("SELECT user_id FROM orders WHERE order_id = ?", (i[3],))
                                        rows = cursor.fetchall()

                                        for j in rows:
                                            await bot.send_message(j[0], f"The supplier is on the way\n\nName: {i[0]}\n\nPhone Number: {i[1]}\n\nCar: {i[2]}")
                break


    conn.close()

    

                                    
                   



@dp.message_handler(lambda message: message.text == "I received the order")
async def deliver_order_received(message: types.Message, state: FSMContext):
    print('Hello')
    deliver_ = message.from_user.id
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("I handed it over to the customer")
    keyboard.add(button)

    deliver_id = "SELECT deliver_id FROM deliverables WHERE deliver_id = ?"


    cursor.execute(deliver_id, (deliver_,))
    row = cursor.fetchall()

    for i in row:
        print(i)
        cursor.execute("SELECT longtude, latitute FROM locations WHERE deliver_id = ?", (i[0],))
        location = cursor.fetchall()
        print(location)
        for j in location:
            print(j[1], j[0])


            await message.answer('The address you need to deliver to', reply_markup=keyboard)
            # Replace location.latitude and location.longitude with actual latitude and longitude values
            await bot.send_location(i[0], latitude=j[1], longitude=j[0])
        conn.close()

@dp.message_handler(lambda message: message.text == "I handed it over to the customer")
async def finish_order(message: types.Message, state: FSMContext):
    del_id = message.from_user.id

    conn = sqlite3.connect('data.db')

    cursor = conn.cursor()

    update_status_del = "UPDATE deliverables SET deliver_status = ?, status = ? WHERE deliver_id = ?"
    cursor.execute(update_status_del, ("empty", "finished", del_id))
    conn.commit()
    await message.answer("Ok wait for next")


@dp.message_handler(lambda message: message.text == "Take away🫴")
async def take_away(message: types.Message, state: FSMContext):
    pass

        
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
        button = [[KeyboardButton(text="Return to top🔙")]]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)

        await message.answer(f"In your account has {row[0]}$", reply_markup=keyboard)




            





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
        # Generate 5 unique random 6-digit numbers
        random_number = generate_unique_numbers(1)
        print(random_number)

        for row in rows:

            # Define the SQL query with a WHERE clause to filter rows by product_catalog and product_name
            query = "INSERT INTO orders (user_id, order_name, order_description, order_price, order_id, order_status) VALUES (?, ?, ?, ?, ?, ?)"
            values = (user_id, row[0], row[1], row[2],random_number[0], "Unpaid")
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            button = [[KeyboardButton(text="Return to top🔙")]]
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=button)

            await bot.send_message(user_id, "Product saved to basket", reply_markup=keyboard)
            
        if not rows:  # If no rows were found
            await bot.send_message(callback_query.from_user.id, "Product not found.")
    else:
        await bot.send_message(callback_query.from_user.id, "Catalog not specified.")








if __name__ == "__main__":
    create_database()

    executor.start_polling(dp, skip_updates=True)
