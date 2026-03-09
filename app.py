
from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(BASE_DIR, "accounts.csv")
FIELDS = ["name","address","city","classification"]

def init_file():
    if not os.path.exists(FILE):
        with open(FILE,"w",newline="") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)

def read_accounts():
    accounts=[]
    if os.path.exists(FILE):
        with open(FILE,"r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                accounts.append(row)
    return accounts

def add_account_row(data):
    with open(FILE,"a",newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data)

@app.route("/",methods=["GET"])
def dashboard():
    init_file()
    search=request.args.get("search","").lower()

    accounts=read_accounts()

    if search:
        accounts=[a for a in accounts if search in a["name"].lower() or search in a["city"].lower()]

    return render_template("dashboard.html",accounts=accounts,search=search)


@app.route("/add",methods=["GET","POST"])
def add_account():

    if request.method=="POST":

        name=request.form["name"]
        address=request.form["address"]
        city=request.form["city"]
        classification=request.form["classification"]

        add_account_row([name,address,city,classification])

        return redirect("/")

    return render_template("add.html")


@app.route("/import",methods=["GET","POST"])
def import_csv():

    if request.method=="POST":

        file=request.files["file"]

        if file:
            stream=file.stream.read().decode("UTF8").splitlines()
            reader=csv.reader(stream)

            rows=list(reader)

            with open(FILE,"w",newline="") as f:
                writer=csv.writer(f)
                writer.writerows(rows)

        return redirect("/")

    return render_template("import.html")


if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
