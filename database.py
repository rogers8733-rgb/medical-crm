
import sqlite3

DB="crm.db"

def conn():
    return sqlite3.connect(DB)

def init():
    db=conn()
    c=db.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS accounts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        office_name TEXT,
        address TEXT,
        city TEXT,
        latitude REAL,
        longitude REAL,
        classification TEXT,
        last_visit_date TEXT,
        next_follow_up_date TEXT,
        times_visited INTEGER DEFAULT 0
    )
    ''')

    db.commit()
    db.close()
