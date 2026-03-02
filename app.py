
from flask import Flask, render_template, request, redirect
import csv, os
from datetime import datetime

app = Flask(__name__)

OFFICE_FILE = "accounts.csv"
VISIT_FILE = "visits.csv"
REF_FILE = "referrals.csv"

def read_csv(file):
    rows = []
    try:
        with open(file, "r") as f:
            r = csv.reader(f)
            for x in r:
                rows.append(x)
    except:
        pass
    return rows

def append_csv(file,row):
    with open(file,"a",newline="") as f:
        w = csv.writer(f)
        w.writerow(row)

@app.route("/")
def index():
    offices = read_csv(OFFICE_FILE)
    visits = read_csv(VISIT_FILE)
    refs = read_csv(REF_FILE)
    return render_template("index.html", offices=offices, visits=visits, refs=refs)

@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        office = request.form.get("office","")
        md = request.form.get("md","")
        phone = request.form.get("phone","")
        address = request.form.get("address","")
        notes = request.form.get("notes","")
        today = datetime.today().strftime("%Y-%m-%d")

        append_csv(OFFICE_FILE,[office,md,phone,"C",today,notes,address])
        return redirect("/")

    return render_template("add.html")

@app.route("/visits", methods=["GET","POST"])
def visits():
    offices = read_csv(OFFICE_FILE)

    if request.method == "POST":
        office = request.form.get("office","")
        note = request.form.get("note","")
        today = datetime.today().strftime("%Y-%m-%d")

        append_csv(VISIT_FILE,[office,today,note])
        return redirect("/")

    return render_template("visits.html", offices=offices)

@app.route("/quick_referral", methods=["GET","POST"])
def quick_referral():
    offices = read_csv(OFFICE_FILE)

    if request.method == "POST":
        office = request.form.get("office","")
        rtype = request.form.get("rtype","")
        today = datetime.today().strftime("%Y-%m-%d")

        append_csv(REF_FILE,[office,today,rtype])
        return redirect("/")

    return render_template("quick.html", offices=offices)

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/map")
def map_page():
    offices = read_csv(OFFICE_FILE)
    return render_template("map.html", offices=offices)

@app.route("/visit")
def visit():
    return render_template("visit.html")

@app.route("/referral")
def referral():
    return render_template("referral.html")

@app.route("/referrals")
def referrals():
    return render_template("referrals.html")

@app.route("/notes")
def notes():
    return render_template("notes.html")

@app.route("/office")
def office():
    return render_template("office.html")

@app.route("/today")
def today():
    return render_template("today.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)
