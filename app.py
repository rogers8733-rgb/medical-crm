
from flask import Flask, render_template, request, redirect
import csv, os
from datetime import datetime

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
    if v: return v[-1][1]
    return None

@app.route("/")
def index():
    offices=read_csv(OFFICE_FILE)
    visits=read_csv(VISIT_FILE)
    refs=read_csv(REF_FILE)

    ref_count={}
    for r in refs:
        if r:
            ref_count[r[0]]=ref_count.get(r[0],0)+1

    leaderboard=sorted(ref_count.items(),key=lambda x:x[1],reverse=True)[:5]

    return render_template("index.html",leaderboard=leaderboard)

@app.route("/planner")
def planner():
    offices=read_csv(OFFICE_FILE)
    visits=read_csv(VISIT_FILE)

    results=[]

    for o in offices:
        name=o[0]
        last=last_visit(name,visits)

        days=999
        if last:
            try:
                d=datetime.strptime(last,"%Y-%m-%d")
                days=(datetime.today()-d).days
            except:
                pass

        results.append((name,days))

    results=sorted(results,key=lambda x:x[1],reverse=True)[:15]

    return render_template("planner.html",results=results)

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

@app.route("/referral",methods=["GET","POST"])
def referral():
    offices=read_csv(OFFICE_FILE)

    if request.method=="POST":
        office=request.form["office"]
        rtype=request.form["rtype"]
        notes=request.form["notes"]
        today=datetime.today().strftime("%Y-%m-%d")
        append_csv(REF_FILE,[office,today,rtype,notes])
        return redirect("/")

    return render_template("referral.html",offices=offices)

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
