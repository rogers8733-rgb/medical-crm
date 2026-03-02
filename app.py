
from flask import Flask, render_template, request, redirect
import csv, os
from datetime import datetime
from collections import defaultdict

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

def last_visit(name, visits):
    v = [x for x in visits if x[0] == name]
    if v:
        return v[-1][1]
    return None

@app.route("/")
def index():
    offices = read_csv(OFFICE_FILE)
    visits = read_csv(VISIT_FILE)
    refs = read_csv(REF_FILE)

    ref_counts = defaultdict(int)
    for r in refs:
        if len(r) > 0:
            ref_counts[r[0]] += 1

    leaderboard = sorted(ref_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    weekly = []
    for o in offices:
        name = o[0]

        last = last_visit(name, visits)

        days = 999
        if last:
            try:
                d = datetime.strptime(last,"%Y-%m-%d")
                days = (datetime.today() - d).days
            except:
                pass

        weekly.append((name, days))

    weekly = sorted(weekly, key=lambda x: x[1], reverse=True)[:5]

    return render_template("index.html", weekly=weekly, leaderboard=leaderboard)

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

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/map")
def map_page():
    offices = read_csv(OFFICE_FILE)
    return render_template("map.html", offices=offices)

if __name__ == "__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)
