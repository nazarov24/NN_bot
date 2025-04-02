import sqlite3

def create_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE NOT NULL,
            phone_number TEXT NOT NULL,
            city TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            address TEXT NOT NULL,
            UNIQUE(chat_id, address)
        )
    ''')
    
    conn.commit()
    conn.close()

create_db()

def get_user_data(chat_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT phone_number, city FROM users WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, None)

def save_user(chat_id, phone_number):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (chat_id, phone_number) VALUES (?, ?)", (chat_id, phone_number))
    conn.commit()
    conn.close()

def update_user_city(chat_id, city):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET city = ? WHERE chat_id = ?", (city, chat_id))
    conn.commit()
    conn.close()

def get_saved_addresses(chat_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT address FROM addresses WHERE chat_id = ?", (chat_id,))
    addresses = [row[0] for row in cursor.fetchall()]
    conn.close()
    return addresses

def save_address(chat_id, address):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO addresses (chat_id, address) VALUES (?, ?)", (chat_id, address))
    conn.commit()
    conn.close()
