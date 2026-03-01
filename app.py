
from flask import Flask, render_template, request, redirect, send_file
import csv, os, zipfile
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

OFFICE_FILE="accounts.csv"
VISIT_FILE="visits.csv"
REF_FILE="referrals.csv"

RULES={"A":14,"B":30,"C":60,"D":120}

def read_csv(file):
    rows=[]
    try:
        with open(file,"r") as f:
            r=csv.reader(f)
            for x in r: rows.append(x)
    except: pass
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

    office_rows=[]
    next_visits=[]
    conversions=[]

    for o in offices:
        name,md,phone,cls,added,notes,address=o
        last=last_visit(name,visits)

        visit_count=len([v for v in visits if v[0]==name])
        ref_count=len([r for r in refs if r[0]==name])

        conv=0
        if visit_count>0:
            conv=round((ref_count/visit_count)*100,1)

        conversions.append((name,conv))

        if last:
            d=datetime.strptime(last,"%Y-%m-%d")
            due=d+timedelta(days=RULES.get(cls,60))
            if due<=datetime.today():
                next_visits.append(name)
        else:
            next_visits.append(name)

        office_rows.append({
            "name":name,"md":md,"phone":phone,
            "class":cls,"notes":notes,"address":address,
            "last_visit":last if last else "None"
        })

    conversions=sorted(conversions,key=lambda x:x[1],reverse=True)

    return render_template("index.html",
        offices=office_rows,
        next_visits=next_visits,
        predictions=conversions[:5],
        total_offices=len(offices),
        total_visits=len(visits),
        total_refs=len(refs)
    )

@app.route("/quick_referral",methods=["GET","POST"])
def quick():
    offices=read_csv(OFFICE_FILE)

    if request.method=="POST":
        office=request.form["office"]
        rtype=request.form["rtype"]
        today=datetime.today().strftime("%Y-%m-%d")
        append_csv(REF_FILE,[office,today,rtype,""])
        return redirect("/quick_referral")

    return render_template("quick.html",offices=offices)

@app.route("/map")
def map():
    offices=read_csv(OFFICE_FILE)
    return render_template("map.html",offices=offices)

@app.route("/backup")
def backup():
    files=[OFFICE_FILE,VISIT_FILE,REF_FILE]
    zipname="crm_backup.zip"
    with zipfile.ZipFile(zipname,"w") as z:
        for f in files:
            if os.path.exists(f): z.write(f)
    return send_file(zipname,as_attachment=True)

@app.route("/add",methods=["GET","POST"])
def add():
    if request.method=="POST":
        office=request.form["office"]
        md=request.form["md"]
        phone=request.form["phone"]
        cls=request.form["classification"]
        notes=request.form["notes"]
        address=request.form["address"]
        today=datetime.today().strftime("%Y-%m-%d")
        append_csv(OFFICE_FILE,[office,md,phone,cls,today,notes,address])
        return redirect("/")
    return render_template("add.html")

if __name__=="__main__":
    app.run(debug=True)
