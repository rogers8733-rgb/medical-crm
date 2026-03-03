
from flask import Flask, render_template, request, redirect, send_file
import csv, os
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

OFFICE_FILE = "accounts.csv"
VISIT_FILE = "visits.csv"
REF_FILE = "referrals.csv"

# ensure files exist
for f in [OFFICE_FILE, VISIT_FILE, REF_FILE]:
    if not os.path.exists(f):
        open(f,"a").close()

cache={"offices":[],"visits":[],"refs":[]}

def read_csv(file):
    rows=[]
    try:
        with open(file,"r",newline="") as f:
            r=csv.reader(f)
            for x in r:
                rows.append(x)
    except:
        pass
    return rows

def load_cache():
    cache["offices"]=read_csv(OFFICE_FILE)
    cache["visits"]=read_csv(VISIT_FILE)
    cache["refs"]=read_csv(REF_FILE)

def append_csv(file,row):
    with open(file,"a",newline="") as f:
        w=csv.writer(f)
        w.writerow(row)
        f.flush()
        os.fsync(f.fileno())
    load_cache()

def write_csv(file,rows):
    with open(file,"w",newline="") as f:
        w=csv.writer(f)
        w.writerows(rows)
    load_cache()

def last_visit(name):
    v=[x for x in cache["visits"] if len(x)>1 and x[0]==name]
    if v:
        return v[-1][1]
    return None

# auto rank
def update_ranks():
    refs=cache["refs"]
    offices=cache["offices"]
    cutoff=datetime.today()-timedelta(days=90)
    counts={}

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

@app.route("/")
def index():
    load_cache()
    update_ranks()
    return render_template("index.html",offices=cache["offices"])

# -------- IMPORT OFFICES --------
@app.route("/import",methods=["GET","POST"])
def import_offices():
    if request.method=="POST":
        file=request.files.get("file")
        if file:
            data=file.read().decode("utf-8").splitlines()
            reader=csv.reader(data)
            today=datetime.today().strftime("%Y-%m-%d")
            next(reader,None)
            for row in reader:
                if len(row)>=5:
                    office=row[0]
                    source_type=row[1]
                    phone=row[2]
                    address=row[3]
                    notes=row[4]
                    append_csv(OFFICE_FILE,[office,source_type,phone,"C",today,notes,address])
        return redirect("/")
    return render_template("import.html")

# search
@app.route("/search")
def search():
    q=request.args.get("q","").lower()
    results=[o for o in cache["offices"] if q in o[0].lower()]
    return render_template("search.html",results=results,q=q)

# add office
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

# quick visit
@app.route("/quickvisit/<office>")
def quickvisit(office):
    today=datetime.today().strftime("%Y-%m-%d")
    append_csv(VISIT_FILE,[office,today,"Quick Visit"])
    return redirect("/office/"+office)

# quick referral
@app.route("/quickref/<office>/<rtype>")
def quickref(office,rtype):
    today=datetime.today().strftime("%Y-%m-%d")
    append_csv(REF_FILE,[office,today,rtype,"Quick Referral"])
    update_ranks()
    return redirect("/office/"+office)

# referral form
@app.route("/referral",methods=["GET","POST"])
def referral():
    if request.method=="POST":
        office=request.form.get("office","")
        rtype=request.form.get("rtype","")
        notes=request.form.get("notes","")
        today=datetime.today().strftime("%Y-%m-%d")
        append_csv(REF_FILE,[office,today,rtype,notes])
        update_ranks()
        return redirect("/planner")
    return render_template("referral.html",offices=cache["offices"])

# planner
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
        results.append((name,rank,days))
    results=sorted(results,key=lambda x:(x[1],-x[2]))
    return render_template("planner.html",results=results)

# top referrals
@app.route("/top")
def top():
    counts=defaultdict(int)
    for r in cache["refs"]:
        if len(r)>=3:
            counts[r[0]]+=1
    top=sorted(counts.items(),key=lambda x:x[1],reverse=True)[:10]
    return render_template("top.html",top=top)

# office page
@app.route("/office/<name>")
def office(name):
    office_data=None
    for o in cache["offices"]:
        if o[0]==name:
            office_data=o
    visits=[v for v in cache["visits"] if len(v)>1 and v[0]==name]
    refs=[r for r in cache["refs"] if len(r)>2 and r[0]==name]
    return render_template("office.html",office=office_data,visits=visits,refs=refs)

# map route planner
@app.route("/map")
def map_page():
    return render_template("map.html",offices=cache["offices"])

# backups
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
