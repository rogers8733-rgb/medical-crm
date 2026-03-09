
from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "crm.db"

def get_conn():
    return sqlite3.connect(DB)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        office TEXT,
        md TEXT,
        coordinator TEXT,
        phone TEXT,
        classification TEXT,
        last_visit TEXT,
        next_followup TEXT,
        notes TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        date TEXT,
        notes TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        patient TEXT,
        date TEXT,
        notes TEXT
    )""")

    conn.commit()
    conn.close()

# Ensure tables exist for Render/Gunicorn
init_db()

@app.route("/", methods=["GET"])
def dashboard():
    search = request.args.get("search","")
    conn = get_conn()
    c = conn.cursor()

    if search:
        q = "%" + search + "%"
        c.execute("""
        SELECT * FROM accounts
        WHERE office LIKE ? OR md LIKE ? OR coordinator LIKE ?
        """,(q,q,q))
    else:
        c.execute("SELECT * FROM accounts")

    accounts = c.fetchall()

    today = datetime.today().strftime("%Y-%m-%d")
    c.execute("SELECT * FROM accounts WHERE next_followup != '' AND next_followup <= ?",(today,))
    followups = c.fetchall()

    conn.close()

    return render_template("dashboard.html",accounts=accounts,followups=followups,search=search)


@app.route("/add",methods=["GET","POST"])
def add_account():

    if request.method == "POST":

        data=(
        request.form["office"],
        request.form["md"],
        request.form["coordinator"],
        request.form["phone"],
        request.form["classification"],
        request.form["last_visit"],
        request.form["next_followup"],
        request.form["notes"]
        )

        conn=get_conn()
        c=conn.cursor()

        c.execute("""
        INSERT INTO accounts
        (office,md,coordinator,phone,classification,last_visit,next_followup,notes)
        VALUES (?,?,?,?,?,?,?,?)
        """,data)

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_account.html")


@app.route("/visit/<int:id>",methods=["GET","POST"])
def log_visit(id):

    if request.method=="POST":

        conn=get_conn()
        c=conn.cursor()

        c.execute("INSERT INTO visits (account_id,date,notes) VALUES (?,?,?)",
        (id,request.form["date"],request.form["notes"]))

        c.execute("UPDATE accounts SET last_visit=? WHERE id=?",
        (request.form["date"],id))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("visit.html",id=id)


@app.route("/referral/<int:id>",methods=["GET","POST"])
def log_referral(id):

    if request.method=="POST":

        conn=get_conn()
        c=conn.cursor()

        c.execute("INSERT INTO referrals (account_id,patient,date,notes) VALUES (?,?,?,?)",
        (id,request.form["patient"],request.form["date"],request.form["notes"]))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("referral.html",id=id)


if __name__=="__main__":
    app.run(debug=True)
