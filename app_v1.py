import sqlite3
from pprint import pprint
#import pandas as pd


# PROGRAMMATICALLY QUERY THE SQLITE3 DATABASE
def db(query):
    conn = sqlite3.connect("car_rental.db")
    cursor = conn.cursor()
    cursor.execute(query)
    cars = cursor.fetchall()
    conn.close()
    pprint(cars)

# LIKE QUERY SQLITE3
def db_like(search_term):
    conn = sqlite3.connect("car_rental.db")
    cursor = conn.cursor()

    pattern = f"%{search_term}%"
    total_query = "SELECT * FROM cars WHERE is_available = 1 AND car_code LIKE ?"

    cursor.execute(total_query, (pattern,))
    results = cursor.fetchall()

    for row in results:
        print(row)

    conn.close()


# LIST ALL AVAILABLE CARS
def list_available():
    db(query='''
             SELECT car_code, make, model, year, daily_rate
             FROM cars
             WHERE is_available = TRUE
             ORDER BY make, model
             ''')


def rent_a_car():
    list_available()
    search = input("Enter car code: ")
    db_like(search)


# FIND RECORDS BASED ON DICT KEYWORDS e.g. FIND CARS where YEAR = 2010
def find(key):
    print("query database based on " + key)


# INSTRUCTIONS FOR USERS
def help_menu():
    print("\nLIST or ls -- list all available cars")
    print("RENT -- rent an available car")
    print("RETURN -- return a rented car")
    print("FIND  -- query the database via keywords")



# MAIN PROGRAM
print("\nWelcome to Global Car Rental Management System")


# MAIN COMMAND LOGIC
x = "0"


while x != "exit":
    x = input("\nlist, rent, return, find, help, or exit: ").lower()

    if x in ["list", "ls"]:
        list_available()
    elif x == "rent":
        print("Renting new car ..")
        rent_a_car()
    elif x == "return":
        print("Returning a car ..")
    elif x == "find":
        # DEVELOP THIS TO INCORPORATE MULTI KEYWORDS
        term = input(" :: ").lower()
        find(term)
    elif x == "help":
        help_menu()
    elif x == "exit":
        break

print("Thank you for using the Global Car Rental Management System. Goodbye")