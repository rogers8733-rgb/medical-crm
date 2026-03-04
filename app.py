
from flask import Flask,render_template,request,redirect
from database import conn,init
from datetime import datetime
import csv

app=Flask(__name__)
init()

@app.route("/")
def dashboard():
    db=conn()

    total=db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]

    overdue=db.execute(
        "SELECT id,office_name FROM accounts WHERE last_visit_date IS NULL OR last_visit_date<=date('now','-60 day')"
    ).fetchall()

    top=db.execute(
        "SELECT accounts.office_name, COUNT(referrals.id) "
        "FROM referrals JOIN accounts ON referrals.account_id=accounts.id "
        "GROUP BY accounts.id ORDER BY COUNT(referrals.id) DESC LIMIT 5"
    ).fetchall()

    db.close()

    return render_template("dashboard.html",total=total,overdue=overdue,top=top)


@app.route("/assistant")
def assistant():
    db=conn()

    suggestions=[]

    overdue=db.execute(
        "SELECT office_name FROM accounts WHERE last_visit_date IS NULL OR last_visit_date<=date('now','-60 day') LIMIT 5"
    ).fetchall()

    for o in overdue:
        suggestions.append(f"Visit {o[0]} (not visited in 60+ days)")

    top=db.execute(
        "SELECT accounts.office_name, COUNT(referrals.id) "
        "FROM referrals JOIN accounts ON referrals.account_id=accounts.id "
        "GROUP BY accounts.id ORDER BY COUNT(referrals.id) DESC LIMIT 3"
    ).fetchall()

    for t in top:
        suggestions.append(f"Maintain relationship with {t[0]} – high referral source")

    low=db.execute(
        "SELECT accounts.office_name, COUNT(referrals.id) "
        "FROM accounts LEFT JOIN referrals ON referrals.account_id=accounts.id "
        "GROUP BY accounts.id ORDER BY COUNT(referrals.id) ASC LIMIT 3"
    ).fetchall()

    for l in low:
        suggestions.append(f"Opportunity: educate {l[0]} on equipment options")

    db.close()

    return render_template("assistant.html",suggestions=suggestions)


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
        notes=request.form["notes"]

        db=conn()

        db.execute(
            "INSERT INTO visits(account_id,date,who,visit_type,notes) VALUES(?,?,?,?,?)",
            (id,datetime.now().strftime("%Y-%m-%d"),who,vtype,notes)
        )

        db.execute(
            "UPDATE accounts SET last_visit_date=date('now') WHERE id=?",
            (id,)
        )

        db.commit()
        db.close()

        return redirect("/accounts")

    return render_template("visit.html",id=id)


@app.route("/referral/<id>",methods=["POST"])
def referral(id):

    patient=request.form["patient"]
    cat=request.form["category"]
    status=request.form["status"]

    db=conn()

    db.execute(
        "INSERT INTO referrals(account_id,patient,category,status,date) VALUES(?,?,?,?,date('now'))",
        (id,patient,cat,status)
    )

    db.commit()
    db.close()

    return redirect("/accounts")


@app.route("/map")
def map_view():
    db=conn()
    rows=db.execute("SELECT id,office_name,latitude,longitude,address,city FROM accounts WHERE latitude IS NOT NULL").fetchall()
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
                "INSERT INTO accounts(office_name,address,city,classification) VALUES(?,?,?,?)",
                (r.get("office_name"),r.get("address"),r.get("city"),r.get("classification","C"))
            )

        db.commit()
        db.close()

        return redirect("/accounts")

    return render_template("import.html")
