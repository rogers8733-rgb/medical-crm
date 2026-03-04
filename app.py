
from flask import Flask,render_template,request,redirect
from datetime import datetime,timedelta
import csv
from database import conn,init
from utils import optimize_route

app=Flask(__name__)
init()

@app.route("/")
def home():
    db=conn()
    total=db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    due=db.execute("SELECT COUNT(*) FROM accounts WHERE next_follow_up_date<=date('now')").fetchone()[0]
    db.close()
    return render_template("home.html",total=total,due=due)

@app.route("/auto-route",methods=["POST"])
def auto_route():

    lat=float(request.form["lat"])
    lon=float(request.form["lon"])

    db=conn()

    rows=db.execute(
        "SELECT id,office_name,address,city,latitude,longitude,next_follow_up_date "
        "FROM accounts WHERE next_follow_up_date<=date('now') AND latitude IS NOT NULL"
    ).fetchall()

    db.close()

    pts=[]

    for r in rows:
        pts.append({
            "id":r[0],
            "name":r[1],
            "address":r[2],
            "city":r[3],
            "lat":r[4],
            "lon":r[5]
        })

    ordered=optimize_route(lat,lon,pts)

    return render_template("route.html",stops=ordered)

@app.route("/visit/<id>",methods=["GET","POST"])
def visit(id):

    if request.method=="POST":

        who=request.form["who"]
        vtype=request.form["type"]
        notes=request.form["notes"]

        db=conn()

        db.execute(
            "INSERT INTO visits(account_id,date,who,visit_type,notes) VALUES(date('now'),?,?,?,?)",
            (id,who,vtype,notes)
        )

        db.execute(
            "UPDATE accounts SET last_visit_date=date('now'),next_follow_up_date=date('now','+30 day') WHERE id=?",
            (id,)
        )

        db.commit()
        db.close()

        return redirect("/")

    return render_template("visit.html",id=id)

@app.route("/accounts")
def accounts():
    db=conn()
    rows=db.execute("SELECT * FROM accounts").fetchall()
    db.close()
    return render_template("accounts.html",accounts=rows)
