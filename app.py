
from flask import Flask, render_template, request, redirect, send_file
import csv, os, zipfile
from datetime import datetime, timedelta

app = Flask(__name__)

OFFICE_FILE = "accounts.csv"
VISIT_FILE = "visits.csv"
REF_FILE = "referrals.csv"

RULES = {"A":14,"B":30,"C":60,"D":120}


def read_csv(file):
    rows = []
    try:
        with open(file,"r") as f:
            reader = csv.reader(f)
            for r in reader:
                rows.append(r)
    except:
        pass
    return rows


def append_csv(file,row):
    with open(file,"a",newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def last_visit(name,visits):
    v = [x for x in visits if x[0] == name]
    if v:
        return v[-1][1]
    return None


@app.route("/")
def index():

    offices = read_csv(OFFICE_FILE)
    visits = read_csv(VISIT_FILE)
    refs = read_csv(REF_FILE)

    next_visits = []

    for o in offices:
        name, md, phone, cls, added, notes, address = o

        last = last_visit(name, visits)

        if last:
            d = datetime.strptime(last,"%Y-%m-%d")
            due = d + timedelta(days=RULES.get(cls,60))

            if due <= datetime.today():
                next_visits.append(name)

        else:
            next_visits.append(name)

    return render_template(
        "index.html",
        total_offices=len(offices),
        total_refs=len(refs),
        next_visits=next_visits
    )


@app.route("/quick_referral",methods=["GET","POST"])
def quick():

    offices = read_csv(OFFICE_FILE)

    if request.method == "POST":

        office = request.form["office"]
        rtype = request.form["rtype"]

        today = datetime.today().strftime("%Y-%m-%d")

        append_csv(REF_FILE,[office,today,rtype,""])

        return redirect("/")

    return render_template("quick.html", offices=offices)


@app.route("/add",methods=["GET","POST"])
def add():

    if request.method == "POST":

        office = request.form["office"]
        md = request.form["md"]
        phone = request.form["phone"]
        address = request.form["address"]
        cls = request.form["classification"]
        notes = request.form["notes"]

        today = datetime.today().strftime("%Y-%m-%d")

        append_csv(OFFICE_FILE,[office,md,phone,cls,today,notes,address])

        return redirect("/")

    return render_template("add.html")


@app.route("/map")
def map_page():
    return render_template("map.html")


@app.route("/backup")
def backup():

    zipname = "crm_backup.zip"

    with zipfile.ZipFile(zipname,"w") as z:

        for f in [OFFICE_FILE,VISIT_FILE,REF_FILE]:
            if os.path.exists(f):
                z.write(f)

    return send_file(zipname,as_attachment=True)


if __name__ == "__main__":
    app.run()
