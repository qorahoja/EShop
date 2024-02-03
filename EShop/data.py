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

        self.conn.commit()

    def close_connection(self):
        self.conn.close()

