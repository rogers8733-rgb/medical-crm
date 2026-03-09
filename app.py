
from flask import Flask,render_template,request,redirect
from database import conn,init
from datetime import datetime
import csv

app=Flask(__name__)
init()

@app.route("/")
def dashboard():
    db=conn()
    accounts=db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    visits=db.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
    referrals=db.execute("SELECT COUNT(*) FROM referrals").fetchone()[0]
    db.close()
    return render_template("dashboard.html",accounts=accounts,visits=visits,referrals=referrals)

@app.route("/accounts")
def accounts():
    db=conn()
    rows=db.execute("SELECT * FROM accounts ORDER BY name").fetchall()
    db.close()
    return render_template("accounts.html",accounts=rows)

@app.route("/add_account",methods=["GET","POST"])
def add_account():
    if request.method=="POST":
        db=conn()
        db.execute(
            "INSERT INTO accounts(name,address,city,classification) VALUES(?,?,?,?)",
            (request.form["name"],request.form["address"],request.form["city"],request.form["classification"])
        )
        db.commit()
        db.close()
        return redirect("/accounts")
    return render_template("add_account.html")

@app.route("/visit/<id>",methods=["GET","POST"])
def visit(id):
    if request.method=="POST":
        db=conn()
        db.execute(
            "INSERT INTO visits(account_id,date,who,notes) VALUES(?,?,?,?)",
            (id,datetime.now().strftime("%Y-%m-%d"),request.form["who"],request.form["notes"])
        )
        db.commit()
        db.close()
        return redirect("/accounts")
    return render_template("visit.html",id=id)

@app.route("/referral/<id>",methods=["GET","POST"])
def referral(id):
    if request.method=="POST":
        db=conn()
        db.execute(
            "INSERT INTO referrals(account_id,date,category,notes) VALUES(?,?,?,?)",
            (id,datetime.now().strftime("%Y-%m-%d"),request.form["category"],request.form["notes"])
        )
        db.commit()
        db.close()
        return redirect("/accounts")
    return render_template("referral.html",id=id)

@app.route("/map")
def map_view():
    db=conn()
    rows=db.execute("SELECT name,latitude,longitude,address,city FROM accounts WHERE latitude IS NOT NULL").fetchall()
    db.close()
    return render_template("map.html",rows=rows)

@app.route("/import",methods=["GET","POST"])
def import_csv():
    if request.method=="POST":
        f=request.files["file"]
        reader=csv.DictReader(f.read().decode().splitlines())
        db=conn()
        for r in reader:
            db.execute(
                "INSERT INTO accounts(name,address,city,classification) VALUES(?,?,?,?)",
                (r.get("name"),r.get("address"),r.get("city"),r.get("classification","C"))
            )
        db.commit()
        db.close()
        return redirect("/accounts")
    return render_template("import.html")
