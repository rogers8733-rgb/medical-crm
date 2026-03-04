
from flask import Flask,render_template,request,redirect
from database import conn,init
from utils import haversine,geocode
from datetime import datetime
import csv

app=Flask(__name__)
init()

@app.route("/")
def dashboard():
    db=conn()

    active=db.execute("SELECT COUNT(*) FROM accounts WHERE active=1").fetchone()[0]
    potential=db.execute("SELECT COUNT(*) FROM accounts WHERE active=0").fetchone()[0]

    overdue=db.execute(
        "SELECT office_name FROM accounts WHERE active=1 AND (last_visit_date IS NULL OR last_visit_date<=date('now','-60 day'))"
    ).fetchall()

    db.close()

    return render_template("dashboard.html",active=active,potential=potential,overdue=overdue)

@app.route("/assistant")
def assistant():
    db=conn()

    suggestions=[]
    overdue=db.execute(
        "SELECT office_name FROM accounts WHERE active=1 AND (last_visit_date IS NULL OR last_visit_date<=date('now','-60 day')) LIMIT 5"
    ).fetchall()

    for o in overdue:
        suggestions.append(f"Visit {o[0]} (not visited in 60+ days)")

    db.close()
    return render_template("assistant.html",suggestions=suggestions)

@app.route("/accounts")
def accounts():
    db=conn()
    rows=db.execute("SELECT * FROM accounts ORDER BY office_name").fetchall()
    db.close()
    return render_template("accounts.html",accounts=rows)

@app.route("/referral/<id>",methods=["POST"])
def referral(id):

    db=conn()

    patient=request.form["patient"]
    category=request.form["category"]
    status=request.form["status"]
    who=request.form["who"]
    notes=request.form["notes"]

    # log referral
    db.execute(
        "INSERT INTO referrals(account_id,patient,category,status,date) VALUES(?,?,?,?,date('now'))",
        (id,patient,category,status)
    )

    # log visit automatically
    db.execute(
        "INSERT INTO visits(account_id,date,who,notes) VALUES(?,?,?,?)",
        (id,datetime.now().strftime("%Y-%m-%d"),who,notes)
    )

    # activate office
    db.execute("UPDATE accounts SET active=1,last_visit_date=date('now') WHERE id=?", (id,))

    # geocode address for that office
    row=db.execute("SELECT address,city FROM accounts WHERE id=?", (id,)).fetchone()
    lat,lon=geocode(f"{row[0]} {row[1]}")
    if lat:
        db.execute("UPDATE accounts SET latitude=?,longitude=? WHERE id=?", (lat,lon,id))

    db.commit()
    db.close()

    return redirect("/accounts")

@app.route("/nearby",methods=["POST"])
def nearby():

    lat=float(request.form["lat"])
    lon=float(request.form["lon"])

    db=conn()
    rows=db.execute(
        "SELECT office_name,address,city,latitude,longitude FROM accounts WHERE active=1 AND latitude IS NOT NULL"
    ).fetchall()
    db.close()

    results=[]
    for r in rows:
        d=haversine(lat,lon,r[3],r[4])
        if d<10:
            results.append((r[0],r[1],r[2],round(d,1)))

    results.sort(key=lambda x:x[3])

    return render_template("nearby.html",rows=results)

@app.route("/map")
def map_view():
    db=conn()
    rows=db.execute(
        "SELECT office_name,latitude,longitude,address,city FROM accounts WHERE active=1 AND latitude IS NOT NULL"
    ).fetchall()
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
                "INSERT INTO accounts(office_name,address,city,classification,active) VALUES(?,?,?,?,0)",
                (r.get("office_name"),r.get("address"),r.get("city"),r.get("classification","C"))
            )

        db.commit()
        db.close()

        return redirect("/accounts")

    return render_template("import.html")
