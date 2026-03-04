
from flask import Flask,render_template,request,redirect,jsonify
import csv,time
from datetime import datetime,timedelta
from database import conn,init
from utils import haversine,geocode_address,optimize_route

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

@app.route("/account/<id>")
def account_detail(id):
    db=conn()
    office=db.execute("SELECT * FROM accounts WHERE id=?",(id,)).fetchone()
    visits=db.execute("SELECT date,who,visit_type,notes FROM visits WHERE account_id=? ORDER BY date DESC",(id,)).fetchall()
    db.close()
    return render_template("account.html",office=office,visits=visits)

@app.route("/visit/<id>",methods=["GET","POST"])
def visit(id):
    if request.method=="POST":
        who=request.form["who"]
        vtype=request.form["type"]
        notes=request.form["notes"]

        db=conn()
        today=datetime.now()

        db.execute(
            "INSERT INTO visits(account_id,date,who,visit_type,notes) VALUES(?,?,?,?,?)",
            (id,today.strftime("%Y-%m-%d"),who,vtype,notes)
        )

        r=db.execute("SELECT classification,times_visited FROM accounts WHERE id=?",(id,)).fetchone()
        next_date=(today+timedelta(days=follow_days(r[0]))).strftime("%Y-%m-%d")

        db.execute(
            "UPDATE accounts SET last_visit_date=?,next_follow_up_date=?,times_visited=? WHERE id=?",
            (today.strftime("%Y-%m-%d"),next_date,r[1]+1,id)
        )

        db.commit()
        db.close()

        return redirect(f"/account/{id}")

    return render_template("visit.html",id=id)

@app.route("/referral/<id>",methods=["POST"])
def referral(id):
    cat=request.form["cat"]
    db=conn()
    db.execute(
        "INSERT INTO referrals(account_id,category,date) VALUES(?,?,?)",
        (id,cat,datetime.now().strftime("%Y-%m-%d"))
    )
    db.commit()
    db.close()
    return redirect(f"/account/{id}")

@app.route("/leaderboard")
def leaderboard():
    db=conn()
    rows=db.execute(
        "SELECT accounts.office_name, COUNT(referrals.id) as total "
        "FROM referrals JOIN accounts ON referrals.account_id=accounts.id "
        "GROUP BY accounts.id ORDER BY total DESC LIMIT 20"
    ).fetchall()
    db.close()
    return render_template("leaderboard.html",rows=rows)

@app.route("/import",methods=["GET","POST"])
def import_csv():
    if request.method=="POST":
        f=request.files["file"]
        reader=csv.DictReader(f.read().decode().splitlines())
        db=conn()
        for r in reader:
            db.execute(
                "INSERT INTO accounts(office_name,address,city,classification) VALUES(?,?,?,?)",
                (r.get("office_name"),r.get("address"),r.get("city"),r.get("classification","C"))
            )
        db.commit()
        db.close()
        return redirect("/accounts")
    return render_template("import.html")

@app.route("/geocode")
def geocode_all():
    db=conn()
    cur=db.cursor()
    rows=cur.execute("SELECT id,address,city FROM accounts WHERE latitude IS NULL").fetchall()

    updated=0
    for r in rows:
        full=f"{r[1]} {r[2]}"
        lat,lon=geocode_address(full)
        if lat and lon:
            cur.execute("UPDATE accounts SET latitude=?,longitude=? WHERE id=?",(lat,lon,r[0]))
            updated+=1
        time.sleep(1)

    db.commit()
    db.close()
    return f"Geocoded {updated} offices"

@app.route("/daily-route",methods=["POST"])
def daily_route():
    lat=request.form["lat"]
    lon=request.form["lon"]

    db=conn()
    rows=db.execute(
        "SELECT id,office_name,latitude,longitude,next_follow_up_date FROM accounts"
    ).fetchall()
    db.close()

    today=datetime.now().strftime("%Y-%m-%d")

    pts=[{"id":r[0],"name":r[1],"lat":r[2],"lon":r[3]} for r in rows if r[2] and r[4] and r[4]<=today]

    ordered=optimize_route(lat,lon,pts)

    return render_template("route.html",accounts=ordered)
