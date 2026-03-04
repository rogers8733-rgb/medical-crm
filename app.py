
from flask import Flask,render_template,request,redirect
from datetime import datetime,timedelta
import csv,time
from database import conn,init
from utils import geocode_address

app=Flask(__name__)
init()

def follow_days(c):
    return {"A":30,"B":45,"C":60,"D":90}.get(c,"60")

@app.route("/")
def home():
    db=conn()
    total=db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    due=db.execute("SELECT COUNT(*) FROM accounts WHERE next_follow_up_date<=date('now')").fetchone()[0]
    db.close()
    return render_template("home.html",total=total,due=due)

@app.route("/accounts")
def accounts():
    db=conn()
    rows=db.execute("SELECT * FROM accounts").fetchall()
    db.close()
    return render_template("accounts.html",accounts=rows)

@app.route("/map")
def map_view():
    db=conn()
    rows=db.execute("SELECT id,office_name,latitude,longitude FROM accounts WHERE latitude IS NOT NULL").fetchall()
    db.close()
    return render_template("map.html",rows=rows)

@app.route("/quickvisit/<id>",methods=["POST"])
def quickvisit(id):
    db=conn()
    today=datetime.now().strftime("%Y-%m-%d")
    db.execute("INSERT INTO visits(account_id,date,who,visit_type,notes) VALUES(?,?,?,?,?)",
               (id,today,"Quick Visit","Drop-in","Logged from map"))
    db.commit()
    db.close()
    return "ok"

@app.route("/visit/<id>",methods=["GET","POST"])
def visit(id):
    if request.method=="POST":
        who=request.form["who"]
        vtype=request.form["type"]
        notes=request.form["notes"]

        db=conn()
        today=datetime.now()

        db.execute("INSERT INTO visits(account_id,date,who,visit_type,notes) VALUES(?,?,?,?,?)",
                   (id,today.strftime("%Y-%m-%d"),who,vtype,notes))

        r=db.execute("SELECT classification,times_visited FROM accounts WHERE id=?",(id,)).fetchone()
        next_date=(today+timedelta(days=follow_days(r[0]))).strftime("%Y-%m-%d")

        db.execute("UPDATE accounts SET last_visit_date=?,next_follow_up_date=?,times_visited=? WHERE id=?",
                   (today.strftime("%Y-%m-%d"),next_date,r[1]+1,id))

        db.commit()
        db.close()
        return redirect("/accounts")

    return render_template("visit.html",id=id)

@app.route("/leaderboard")
def leaderboard():
    db=conn()
    rows=db.execute(
        "SELECT accounts.office_name, COUNT(referrals.id) "
        "FROM referrals JOIN accounts ON referrals.account_id=accounts.id "
        "GROUP BY accounts.id ORDER BY COUNT(referrals.id) DESC"
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
            db.execute("INSERT INTO accounts(office_name,address,city,classification) VALUES(?,?,?,?)",
                       (r.get("office_name"),r.get("address"),r.get("city"),r.get("classification","C")))
        db.commit()
        db.close()
        return redirect("/accounts")
    return render_template("import.html")

@app.route("/geocode")
def geocode():
    db=conn()
    cur=db.cursor()
    rows=cur.execute("SELECT id,address,city FROM accounts WHERE latitude IS NULL").fetchall()
    updated=0
    for r in rows:
        try:
            lat,lon=geocode_address(f"{r[1]} {r[2]}")
            if lat and lon:
                cur.execute("UPDATE accounts SET latitude=?,longitude=? WHERE id=?",(lat,lon,r[0]))
                updated+=1
            db.commit()
            time.sleep(1)
        except:
            pass
    db.close()
    return f"Geocoded {updated} offices"
