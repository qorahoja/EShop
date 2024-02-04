import sqlite3

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_tables(self):

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                uid INTEGER PRIMARY KEY,
                                username TEXT,
                                password TEXT
                            )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                                aid INTEGER PRIMARY KEY,
                                username TEXT,
                                password TEXT
                            )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS catalog(
                            catalog_id INTEGER PRIMARY KEY,
                            catalog_name TEXT
                            )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products(
                            product_id INTEGER PRIMARY KEY,
                            product_catalog TEXT,
                            product_name TEXT,
                            product_description TEXT,
                            product_price TEXT


                            )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS orders(
                            user_id INTEGER PRIMARY KEY,
                            order_name TEXT,
                            order_description TEXT,
                            order_price TEXT    
                            )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS wallet(
                            user_id INTEGER PRIMARY KEY,
                            how_much TEXT
                            )''')
        

        self.conn.commit()

    def close_connection(self):
        self.conn.close()

