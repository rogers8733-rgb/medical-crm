
from flask import Flask,render_template,request,redirect
import csv,time
from datetime import datetime,timedelta
from database import conn,init
from utils import haversine,geocode_address

app=Flask(__name__)
init()

def follow_days(c):
    return {"A":30,"B":45,"C":60,"D":90}.get(c,"60")

@app.route("/")
def home():
    db=conn()
    total=db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    today=datetime.now().strftime("%Y-%m-%d")
    due=db.execute("SELECT COUNT(*) FROM accounts WHERE next_follow_up_date<=?",(today,)).fetchone()[0]
    db.close()
    return render_template("home.html",total=total,due=due)

@app.route("/accounts")
def accounts():
    db=conn()
    rows=db.execute("SELECT * FROM accounts ORDER BY office_name").fetchall()
    db.close()
    return render_template("accounts.html",accounts=rows)

@app.route("/import",methods=["GET","POST"])
def import_csv():
    if request.method=="POST":
        f=request.files["file"]
        reader=csv.DictReader(f.read().decode().splitlines())

        db=conn()

        for r in reader:
            db.execute(
                "INSERT INTO accounts(office_name,address,city,classification) VALUES(?,?,?,?)",
                (
                    r.get("office_name"),
                    r.get("address"),
                    r.get("city"),
                    r.get("classification","C")
                )
            )

        db.commit()
        db.close()

        return redirect("/accounts")

    return render_template("import.html")

@app.route("/geocode")
def geocode_all():
    db=conn()
    cur=db.cursor()

    rows=cur.execute(
        "SELECT id,address,city FROM accounts WHERE latitude IS NULL OR latitude=''"
    ).fetchall()

    updated=0

    for r in rows:
        full_address=f"{r[1]} {r[2]}"
        lat,lon=geocode_address(full_address)

        if lat and lon:
            cur.execute(
                "UPDATE accounts SET latitude=?,longitude=? WHERE id=?",
                (lat,lon,r[0])
            )
            updated+=1

        time.sleep(1)

    db.commit()
    db.close()

    return f"Geocoded {updated} offices"

@app.route("/near",methods=["POST"])
def near():
    lat=request.form["lat"]
    lon=request.form["lon"]

    db=conn()
    rows=db.execute("SELECT office_name,latitude,longitude FROM accounts").fetchall()
    db.close()

    results=[]

    for r in rows:
        if r[1] and r[2]:
            d=haversine(lat,lon,r[1],r[2])
            results.append((r[0],round(d,1),r[1],r[2]))

    results.sort(key=lambda x:x[1])

    return render_template("near.html",accounts=results,lat=lat,lon=lon)
