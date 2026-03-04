
from flask import Flask,render_template,request,redirect
from datetime import datetime,timedelta
import csv
from database import conn,init
from utils import haversine,optimize

app=Flask(__name__)
init()

def follow_days(c):
    return {"A":30,"B":45,"C":60,"D":90}.get(c,60)

@app.route("/")
def home():
    db=conn()
    cur=db.cursor()

    total=cur.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]

    today=datetime.now().strftime("%Y-%m-%d")
    due=cur.execute("SELECT COUNT(*) FROM accounts WHERE next_follow_up_date<=?",(today,)).fetchone()[0]

    db.close()

    return render_template("home.html",total=total,due=due)

@app.route("/accounts")
def accounts():
    db=conn()
    rows=db.execute("SELECT * FROM accounts ORDER BY office_name").fetchall()
    db.close()
    return render_template("accounts.html",accounts=rows)

@app.route("/visit/<id>",methods=["GET","POST"])
def visit(id):
    if request.method=="POST":
        who=request.form["who"]
        vtype=request.form["type"]

        db=conn()
        today=datetime.now()

        db.execute(
            "INSERT INTO visits(account_id,date,who,visit_type) VALUES(?,?,?,?)",
            (id,today.strftime("%Y-%m-%d"),who,vtype)
        )

        r=db.execute("SELECT classification,times_visited FROM accounts WHERE id=?",(id,)).fetchone()

        next_date=(today+timedelta(days=follow_days(r[0]))).strftime("%Y-%m-%d")

        db.execute(
            "UPDATE accounts SET last_visit_date=?,next_follow_up_date=?,times_visited=? WHERE id=?",
            (today.strftime("%Y-%m-%d"),next_date,r[1]+1,id)
        )

        db.commit()
        db.close()

        return redirect("/")

    return render_template("visit.html",id=id)

@app.route("/referral/<id>",methods=["GET","POST"])
def referral(id):
    if request.method=="POST":
        cat=request.form["cat"]

        db=conn()
        db.execute(
            "INSERT INTO referrals(account_id,category,date) VALUES(?,?,?)",
            (id,cat,datetime.now().strftime("%Y-%m-%d"))
        )
        db.commit()
        db.close()

        return redirect("/")

    return render_template("referral.html",id=id)

@app.route("/today")
def today():
    db=conn()
    rows=db.execute(
        "SELECT * FROM accounts WHERE next_follow_up_date<=date('now')"
    ).fetchall()
    db.close()

    return render_template("today.html",accounts=rows)

@app.route("/near",methods=["POST"])
def near():
    lat=request.form["lat"]
    lon=request.form["lon"]
    radius=10

    db=conn()
    rows=db.execute("SELECT * FROM accounts").fetchall()
    db.close()

    results=[]
    for r in rows:
        if r[5] and r[6]:
            d=haversine(lat,lon,r[5],r[6])
            if d<=radius:
                results.append({"id":r[0],"name":r[1],"lat":r[5],"lon":r[6],"dist":round(d,1)})

    results.sort(key=lambda x:x["dist"])

    return render_template("near.html",accounts=results,lat=lat,lon=lon)

@app.route("/route",methods=["POST"])
def route():
    lat=request.form["lat"]
    lon=request.form["lon"]

    db=conn()
    rows=db.execute("SELECT id,office_name,latitude,longitude FROM accounts").fetchall()
    db.close()

    pts=[{"id":r[0],"name":r[1],"latitude":r[2],"longitude":r[3]} for r in rows if r[2]]

    ordered=optimize(lat,lon,pts)

    return render_template("route.html",accounts=ordered)

@app.route("/import",methods=["GET","POST"])
def import_csv():
    if request.method=="POST":
        f=request.files["file"]
        reader=csv.DictReader(f.read().decode().splitlines())

        db=conn()

        for r in reader:
            db.execute(
                "INSERT INTO accounts(office_name,address,city,latitude,longitude,classification) VALUES(?,?,?,?,?,?)",
                (
                    r.get("office_name"),
                    r.get("address"),
                    r.get("city"),
                    r.get("latitude"),
                    r.get("longitude"),
                    "C"
                )
            )

        db.commit()
        db.close()

        return redirect("/accounts")

    return render_template("import.html")

if __name__=="__main__":
    app.run()
