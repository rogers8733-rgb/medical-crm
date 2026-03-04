
import sqlite3
DB="crm.db"

def conn():
    return sqlite3.connect(DB)

def init():
    db=conn()
    c=db.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS accounts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        office_name TEXT,
        address TEXT,
        city TEXT,
        latitude REAL,
        longitude REAL,
        classification TEXT,
        active INTEGER DEFAULT 0,
        last_visit_date TEXT
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
        patient TEXT,
        category TEXT,
        status TEXT,
        date TEXT
    )''')

    db.commit()
    db.close()
