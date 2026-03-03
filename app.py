
from flask import Flask, render_template, request, redirect, send_file
import csv, os
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

OFFICE_FILE = "accounts.csv"
VISIT_FILE = "visits.csv"
REF_FILE = "referrals.csv"

# ---------- FILE SAFETY ----------
for f in [OFFICE_FILE, VISIT_FILE, REF_FILE]:
    if not os.path.exists(f):
        open(f,"a").close()

# ---------- CACHE STRUCTURE (performance improvement) ----------
cache = {
    "offices": [],
    "visits": [],
    "refs": []
}

def load_cache():
    cache["offices"] = read_csv(OFFICE_FILE)
    cache["visits"] = read_csv(VISIT_FILE)
    cache["refs"] = read_csv(REF_FILE)

def read_csv(file):
    rows=[]
    try:
        with open(file,"r",newline="") as f:
            reader=csv.reader(f)
            for r in reader:
                rows.append(r)
    except:
        pass
    return rows

def append_csv(file,row):
    with open(file,"a",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(row)
        f.flush()
        os.fsync(f.fileno())
    load_cache()

def write_csv(file,rows):
    with open(file,"w",newline="") as f:
        writer=csv.writer(f)
        writer.writerows(rows)
    load_cache()

def last_visit(name):
    v=[x for x in cache["visits"] if len(x)>1 and x[0]==name]
    if v:
        return v[-1][1]
    return None

# ---------- AUTO ACCOUNT RANK ----------
def update_ranks():
    refs = cache["refs"]
    offices = cache["offices"]

    cutoff = datetime.today() - timedelta(days=90)
    counts = {}

    for r in refs:
        if len(r)<3: continue
        try:
            d=datetime.strptime(r[1],"%Y-%m-%d")
        except:
            continue
        if d>=cutoff:
            counts[r[0]]=counts.get(r[0],0)+1

    new=[]
    for o in offices:
        if len(o)<7:
            new.append(o)
            continue
        c=counts.get(o[0],0)
        rank="D"
        if c>=5: rank="A"
        elif c>=2: rank="B"
        elif c>=1: rank="C"
        o[3]=rank
        new.append(o)

    write_csv(OFFICE_FILE,new)

# ---------- HOME ----------
@app.route("/")
def index():
    load_cache()
    update_ranks()
    offices = cache["offices"]
    return render_template("index.html",offices=offices)

# ---------- SEARCH ----------
@app.route("/search")
def search():
    q=request.args.get("q","").lower()
    results=[o for o in cache["offices"] if q in o[0].lower()]
    return render_template("search.html",results=results,q=q)

# ---------- ADD OFFICE ----------
@app.route("/add",methods=["GET","POST"])
def add():
    if request.method=="POST":
        office=request.form.get("office","")
        phone=request.form.get("phone","")
        address=request.form.get("address","")
        notes=request.form.get("notes","")
        rank=request.form.get("rank","C")
        today=datetime.today().strftime("%Y-%m-%d")

        append_csv(OFFICE_FILE,[office,"",phone,rank,today,notes,address])

        return redirect("/")

    return render_template("add.html")

# ---------- VISIT ----------
@app.route("/quickvisit/<office>")
def quickvisit(office):
    today=datetime.today().strftime("%Y-%m-%d")
    append_csv(VISIT_FILE,[office,today,"Quick Visit"])
    return redirect("/office/"+office)

# ---------- QUICK REFERRAL ----------
@app.route("/quickref/<office>/<rtype>")
def quickref(office,rtype):
    today=datetime.today().strftime("%Y-%m-%d")
    append_csv(REF_FILE,[office,today,rtype,"Quick Referral"])
    update_ranks()
    return redirect("/office/"+office)

# ---------- REFERRAL PAGE ----------
@app.route("/referral",methods=["GET","POST"])
def referral():
    offices=cache["offices"]
    if request.method=="POST":
        office=request.form.get("office","")
        rtype=request.form.get("rtype","")
        notes=request.form.get("notes","")
        today=datetime.today().strftime("%Y-%m-%d")

        append_csv(REF_FILE,[office,today,rtype,notes])
        update_ranks()
        return redirect("/planner")

    return render_template("referral.html",offices=offices)

# ---------- TODAY'S STOPS ----------
@app.route("/planner")
def planner():
    update_ranks()

    results=[]
    for o in cache["offices"]:
        name=o[0]
        rank=o[3] if len(o)>3 else "C"

        last=last_visit(name)
        days=999

        if last:
            try:
                d=datetime.strptime(last,"%Y-%m-%d")
                days=(datetime.today()-d).days
            except:
                pass

        limit=90
        if rank=="A": limit=30
        elif rank=="B": limit=60
        elif rank=="C": limit=90
        elif rank=="D": limit=180

        overdue=days>=limit
        results.append((name,rank,days,overdue))

    results=sorted(results,key=lambda x:(x[1],-x[2]))

    return render_template("planner.html",results=results)

# ---------- TOP REFERRALS ----------
@app.route("/top")
def top():
    counts=defaultdict(int)
    for r in cache["refs"]:
        if len(r)>=3:
            counts[r[0]]+=1

    top=sorted(counts.items(),key=lambda x:x[1],reverse=True)[:10]

    return render_template("top.html",top=top)

# ---------- OFFICE PROFILE ----------
@app.route("/office/<name>")
def office(name):
    office_data=None
    for o in cache["offices"]:
        if o[0]==name:
            office_data=o

    visits=[v for v in cache["visits"] if len(v)>1 and v[0]==name]
    refs=[r for r in cache["refs"] if len(r)>2 and r[0]==name]

    return render_template(
        "office.html",
        office=office_data,
        visits=visits,
        refs=refs
    )

# ---------- MAP ----------
@app.route("/map")
def map_page():
    offices=cache["offices"]
    return render_template("map.html",offices=offices)

# ---------- BACKUP ----------
@app.route("/backup/<file>")
def backup(file):
    if file=="accounts":
        return send_file(OFFICE_FILE,as_attachment=True)
    if file=="visits":
        return send_file(VISIT_FILE,as_attachment=True)
    if file=="referrals":
        return send_file(REF_FILE,as_attachment=True)
    return redirect("/")

if __name__=="__main__":
    load_cache()
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
