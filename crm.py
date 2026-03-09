
import csv
import os

FILE = "accounts.csv"
FIELDS = ["name","address","city","classification"]

def init_file():
    if not os.path.exists(FILE):
        with open(FILE,"w",newline="") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)

def add_account():
    print("\nAdd New Account")
    name = input("Name: ")
    address = input("Address: ")
    city = input("City: ")
    classification = input("Classification (A/B/C/D): ")

    with open(FILE,"a",newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name,address,city,classification])

    print("Account added.")

def view_accounts():
    print("\nAll Accounts")
    with open(FILE,"r") as f:
        reader = csv.reader(f)
        for row in reader:
            print(" | ".join(row))

def search_accounts():
    term = input("\nSearch name or city: ").lower()

    with open(FILE,"r") as f:
        reader = csv.DictReader(f)

        results = []
        for row in reader:
            if term in row["name"].lower() or term in row["city"].lower():
                results.append(row)

        print("\nSearch Results")
        for r in results:
            print(f'{r["name"]} | {r["address"]} | {r["city"]} | {r["classification"]}')

        if not results:
            print("No accounts found.")

def menu():
    init_file()

    while True:
        print("\n--- SIMPLE CRM V1 ---")
        print("1 Add Account")
        print("2 View Accounts")
        print("3 Search Accounts")
        print("4 Exit")

        choice = input("Select option: ")

        if choice == "1":
            add_account()
        elif choice == "2":
            view_accounts()
        elif choice == "3":
            search_accounts()
        elif choice == "4":
            break
        else:
            print("Invalid option")

menu()
