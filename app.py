
from flask import Flask, render_template, request, redirect
import csv
from datetime import datetime, timedelta
from collections import defaultdict
import os

app = Flask(__name__)

OFFICE_FILE="accounts.csv"
VISIT_FILE="visits.csv"
REF_FILE="referrals.csv"

def read_csv(file):
    rows=[]
    try:
        with open(file,"r") as f:
            r=csv.reader(f)
            for x in r:
                rows.append(x)
    except:
        pass
    return rows

def append_csv(file,row):
    with open(file,"a",newline="") as f:
        w=csv.writer(f)
        w.writerow(row)

def last_visit(name,visits):
    v=[x for x in visits if x[0]==name]
    if v:
        return v[-1][1]
    return None

@app.route("/")
def index():

    offices=read_csv(OFFICE_FILE)
    visits=read_csv(VISIT_FILE)
    refs=read_csv(REF_FILE)

    visit_counts=defaultdict(int)
    ref_counts=defaultdict(int)

    for v in visits:
        visit_counts[v[0]]+=1

    for r in refs:
        ref_counts[r[0]]+=1

    weekly=[]

    for o in offices:
        name=o[0]

        last=last_visit(name,visits)

        days=999
        if last:
            d=datetime.strptime(last,"%Y-%m-%d")
            days=(datetime.today()-d).days

        refs_total=ref_counts[name]

        score=days+(refs_total*5)

        weekly.append((name,days,refs_total,score))

    weekly=sorted(weekly,key=lambda x:x[3],reverse=True)[:6]

    return render_template("index.html",weekly=weekly)

@app.route("/visits",methods=["GET","POST"])
def visits():

    offices=read_csv(OFFICE_FILE)

    if request.method=="POST":
        office=request.form["office"]
        note=request.form["note"]
        today=datetime.today().strftime("%Y-%m-%d")

        append_csv(VISIT_FILE,[office,today,note])

        return redirect("/")

    return render_template("visits.html",offices=offices)

@app.route("/analytics")
def analytics():

    refs=read_csv(REF_FILE)

    type_counts=defaultdict(int)
    month_counts=defaultdict(int)

    for r in refs:
        office,date,rtype=r[0],r[1],r[2]

        type_counts[rtype]+=1
        month=date[:7]+=1

    types=sorted(type_counts.items(),key=lambda x:x[1],reverse=True)
    months=sorted(month_counts.items())

    return render_template("analytics.html",types=types,months=months)

@app.route("/map")
def map_page():

    offices=read_csv(OFFICE_FILE)

    data=[]
    for o in offices:
        name=o[0]
        address=o[6] if len(o)>6 else ""
        data.append((name,address))

    return render_template("map.html",offices=data)

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
