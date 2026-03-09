
import sqlite3
DB="crm.db"

def conn():
    return sqlite3.connect(DB)

def init():
    db=conn()
    c=db.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS accounts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        address TEXT,
        city TEXT,
        classification TEXT,
        latitude REAL,
        longitude REAL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS visits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        date TEXT,
        who TEXT,
        notes TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS referrals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        date TEXT,
        category TEXT,
        notes TEXT
    )''')

    db.commit()
    db.close()
