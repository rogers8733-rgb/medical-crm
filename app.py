
from flask import Flask, render_template, request, redirect
import csv, os, datetime

app = Flask(__name__)

ACCOUNTS_FILE = "accounts.csv"
REFERRALS_FILE = "referrals.csv"
VISITS_FILE = "visits.csv"

ACCOUNT_FIELDS = ["name","address","city","classification"]
REFERRAL_FIELDS = ["date","account","type","notes"]
VISIT_FIELDS = ["date","account","notes"]

def init_file(file, fields):
    if not os.path.exists(file):
        with open(file,"w",newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

init_file(ACCOUNTS_FILE, ACCOUNT_FIELDS)
init_file(REFERRALS_FILE, REFERRAL_FIELDS)
init_file(VISITS_FILE, VISIT_FIELDS)

def read_csv(file):
    with open(file,newline="") as f:
        return list(csv.DictReader(f))

def append_csv(file, fields, row):
    with open(file,"a",newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writerow(row)

@app.route("/", methods=["GET"])
def dashboard():
    search = request.args.get("search","").lower()
    accounts = read_csv(ACCOUNTS_FILE)

    if search:
        accounts = [a for a in accounts if search in a["name"].lower() or search in a["city"].lower()]

    referrals = read_csv(REFERRALS_FILE)[-5:]
    visits = read_csv(VISITS_FILE)[-5:]

    return render_template("dashboard.html", accounts=accounts, referrals=referrals, visits=visits, search=search)

@app.route("/accounts")
def accounts():
    accounts = read_csv(ACCOUNTS_FILE)
    return render_template("accounts.html", accounts=accounts)

@app.route("/add_account", methods=["GET","POST"])
def add_account():
    if request.method == "POST":
        data = {
            "name":request.form["name"],
            "address":request.form["address"],
            "city":request.form["city"],
            "classification":request.form["classification"]
        }
        append_csv(ACCOUNTS_FILE, ACCOUNT_FIELDS, data)
        return redirect("/accounts")
    return render_template("add_account.html")

@app.route("/import", methods=["GET","POST"])
def import_accounts():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            rows = file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(rows)
            with open(ACCOUNTS_FILE,"a",newline="") as f:
                writer = csv.DictWriter(f, fieldnames=ACCOUNT_FIELDS)
                for row in reader:
                    writer.writerow(row)
        return redirect("/accounts")
    return render_template("import.html")

@app.route("/log_referral", methods=["GET","POST"])
def log_referral():
    accounts = read_csv(ACCOUNTS_FILE)
    if request.method == "POST":
        data = {
            "date":str(datetime.date.today()),
            "account":request.form["account"],
            "type":request.form["type"],
            "notes":request.form["notes"]
        }
        append_csv(REFERRALS_FILE, REFERRAL_FIELDS, data)
        return redirect("/")
    return render_template("log_referral.html", accounts=accounts)

@app.route("/log_visit", methods=["GET","POST"])
def log_visit():
    accounts = read_csv(ACCOUNTS_FILE)
    if request.method == "POST":
        data = {
            "date":str(datetime.date.today()),
            "account":request.form["account"],
            "notes":request.form["notes"]
        }
        append_csv(VISITS_FILE, VISIT_FIELDS, data)
        return redirect("/")
    return render_template("log_visit.html", accounts=accounts)

if __name__ == "__main__":
    app.run(debug=True, port=10000)
