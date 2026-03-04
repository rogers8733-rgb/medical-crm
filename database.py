
import sqlite3

DB="crm.db"

def conn():
    return sqlite3.connect(DB)

def init():
    c=conn()
    cur=c.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS accounts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        office_name TEXT,
        phone TEXT,
        address TEXT,
        city TEXT,
        latitude REAL,
        longitude REAL,
        classification TEXT,
        last_visit_date TEXT,
        next_follow_up_date TEXT,
        times_visited INTEGER DEFAULT 0,
        notes TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS referrals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        category TEXT,
        date TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS visits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        date TEXT,
        who TEXT,
        visit_type TEXT
    )
    ''')

    c.commit()
    c.close()
