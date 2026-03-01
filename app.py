from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS offices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            office_name TEXT,
            md_name TEXT,
            coordinator TEXT,
            phone TEXT,
            classification TEXT,
            last_visit TEXT,
            next_followup TEXT,
            referrals INTEGER,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def calculate_followup(classification):
    followup_days = {
        "A": 14,
        "B": 30,
        "C": 60,
        "D": 90
    }
    return followup_days.get(classification, 30)

@app.route("/")
def index():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM offices ORDER BY classification ASC")
    offices = cursor.fetchall()
    conn.close()

    today = datetime.today().strftime("%Y-%m-%d")

    return render_template("index.html", offices=offices, today=today)

@app.route("/add", methods=["GET", "POST"])
def add_office():
    if request.method == "POST":
        office_name = request.form["office_name"]
        md_name = request.form["md_name"]
        coordinator = request.form["coordinator"]
        phone = request.form["phone"]
        classification = request.form["classification"]
        notes = request.form["notes"]

        last_visit = datetime.today()
        next_followup = last_visit + timedelta(days=calculate_followup(classification))

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO offices 
            (office_name, md_name, coordinator, phone, classification, last_visit, next_followup, referrals, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            office_name,
            md_name,
            coordinator,
            phone,
            classification,
            last_visit.strftime("%Y-%m-%d"),
            next_followup.strftime("%Y-%m-%d"),
            0,
            notes
        ))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")

@app.route("/log_visit/<int:office_id>")
def log_visit(office_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT classification FROM offices WHERE id = ?", (office_id,))
    classification = cursor.fetchone()[0]

    last_visit = datetime.today()
    next_followup = last_visit + timedelta(days=calculate_followup(classification))

    cursor.execute("""
        UPDATE offices
        SET last_visit = ?, next_followup = ?
        WHERE id = ?
    """, (
        last_visit.strftime("%Y-%m-%d"),
        next_followup.strftime("%Y-%m-%d"),
        office_id
    ))

    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)