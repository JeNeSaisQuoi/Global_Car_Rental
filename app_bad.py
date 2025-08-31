import sqlite3
import csv
from datetime import datetime
import os

class CarRentalDB:
    def __init__(self, db_name="car_rental.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Create cars table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS cars
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           car_code
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           registration
                           TEXT,
                           year
                           INTEGER,
                           make
                           TEXT
                           NOT
                           NULL,
                           model
                           TEXT
                           NOT
                           NULL,
                           type
                           TEXT,
                           passengers
                           INTEGER,
                           vin
                           TEXT,
                           tech_passport
                           TEXT,
                           color
                           TEXT,
                           fuel
                           TEXT,
                           daily_rate
                           REAL
                           DEFAULT
                           0.0,
                           is_available
                           BOOLEAN
                           DEFAULT
                           1,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Create rentals table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS rentals
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           car_code
                           TEXT
                           NOT
                           NULL,
                           customer_name
                           TEXT
                           NOT
                           NULL,
                           rental_date
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           return_date
                           TIMESTAMP,
                           is_returned
                           BOOLEAN
                           DEFAULT
                           0,
                           FOREIGN
                           KEY
                       (
                           car_code
                       ) REFERENCES cars
                       (
                           car_code
                       )
                           )
                       ''')

        conn.commit()
        conn.close()

    def migrate_csv_to_db(self, csv_file_path):
        """Migrate data from CSV file to SQLite database"""
        if not os.path.exists(csv_file_path):
            print(f"CSV file {csv_file_path} not found!")
            return False

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter='\t')

                print(f"CSV Headers found: {reader.fieldnames}")

                imported_count = 0
                skipped_count = 0

                for row in reader:
                    if not any(row.values()) or not row.get('car_code', '').strip():
                        print("Skipping blank row.")
                        skipped_count += 1
                        continue

                    try:
                        car_code = row.get('car_code', '').strip()
                        registration = row.get('registration', '').strip()
                        year = int(row.get('year', '').strip()) if row.get('year', '').strip().isdigit() else None
                        make = row.get('make', '').strip()
                        model = row.get('model', '').strip()
                        car_type = row.get('type', '').strip()
                        passengers = int(row.get('passengers', '0').strip())  # allow 0
                        vin = row.get('vin', '').strip()
                        tech_passport = row.get('tech_passport', '').strip()
                        color = row.get('color', '').strip()
                        fuel = row.get('fuel', '').strip()
                        available = row.get('available', '').strip().upper() == 'TRUE'

                        # Daily rate from column '1'
                        try:
                            daily_rate = float(row.get('1', '0').strip())
                        except ValueError:
                            daily_rate = 0.0

                        if not car_code or not make or not model:
                            print(
                                f"Skipping row with missing required data - car_code: '{car_code}', make: '{make}', model: '{model}'")
                            skipped_count += 1
                            continue

                        # Insert or replace into DB
                        cursor.execute('''
                            INSERT OR REPLACE INTO cars (
                                car_code, registration, year, make, model, type, passengers,
                                vin, tech_passport, color, fuel, daily_rate, is_available
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            car_code, registration, year, make, model, car_type, passengers,
                            vin, tech_passport, color, fuel, daily_rate, int(available)
                        ))

                        imported_count += 1
                        if imported_count <= 5:
                            print(
                                f"Imported: {car_code} - {year} {make} {model} (${daily_rate}) Available: {available}")

                    except Exception as row_error:
                        print(f"Error processing row: {row}")
                        print(f"Row Error: {row_error}")
                        skipped_count += 1

                conn.commit()
                print(f"\nMigration complete: {imported_count} cars imported, {skipped_count} rows skipped")

        except Exception as e:
            print(f"Error opening CSV: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False
        finally:
            conn.close()

        return True

    def get_available_cars(self):
        """Get all available cars"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT car_code, make, model, year, type, color, fuel, passengers, daily_rate
                       FROM cars
                       WHERE is_available = 1
                       ORDER BY make, model
                       ''')

        get_cars = cursor.fetchall()
        conn.close()
        return get_cars

    def get_car_by_code(self, car_code):
        """Get specific car by code"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT car_code, make, model, year, type, color, fuel, passengers, daily_rate, is_available
                       FROM cars
                       WHERE car_code = ?
                       ''', (car_code,))

        car = cursor.fetchone()
        conn.close()
        return car

    def rent_car(self, car_code, customer_name):
        """Rent a car to a customer"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Check if car is available
            cursor.execute('SELECT is_available FROM cars WHERE car_code = ?', (car_code,))
            result = cursor.fetchone()

            if not result:
                return False, "Car code not found"

            if not result[0]:
                return False, "Car is not available"

            # Create rental record
            cursor.execute('''
                           INSERT INTO rentals (car_code, customer_name, rental_date)
                           VALUES (?, ?, ?)
                           ''', (car_code, customer_name, datetime.now()))

            # Mark car as unavailable
            cursor.execute('''
                           UPDATE cars
                           SET is_available = 0
                           WHERE car_code = ?
                           ''', (car_code,))

            conn.commit()
            return True, "Car rented successfully"

        except Exception as e:
            conn.rollback()
            return False, f"Error renting car: {e}"
        finally:
            conn.close()

    def return_car(self, car_code):
        """Return a rented car"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Check if car is currently rented
            cursor.execute('''
                           SELECT id
                           FROM rentals
                           WHERE car_code = ?
                             AND is_returned = 0
                           ''', (car_code,))

            rental = cursor.fetchone()
            if not rental:
                return False, "Car is not currently rented"

            # Update rental record
            cursor.execute('''
                           UPDATE rentals
                           SET return_date = ?,
                               is_returned = 1
                           WHERE id = ?
                           ''', (datetime.now(), rental[0]))

            # Mark car as available
            cursor.execute('''
                           UPDATE cars
                           SET is_available = 1
                           WHERE car_code = ?
                           ''', (car_code,))

            conn.commit()
            return True, "Car returned successfully"

        except Exception as e:
            conn.rollback()
            return False, f"Error returning car: {e}"
        finally:
            conn.close()


# Initialize database
db = CarRentalDB()


def migrate_csv():
    """Helper function to migrate CSV data"""
    csv_file = input("Enter CSV file path: ").strip()
    if csv_file:
        db.migrate_csv_to_db(csv_file)
    else:
        print("No file path provided")


def list_available():
    print("\nAvailable cars:")
    car = db.get_available_cars()

    if not cars:
        print("No cars available")
        return None

    print(
        f"{'Code':<12} {'Make':<12} {'Model':<15} {'Year':<6} {'Type':<12} {'Color':<8} {'Fuel':<8} {'Pass.':<5} {'Rate':<8}")
    print("-" * 88)

    for car in cars:
        car_code, make, model, year, car_type, color, fuel, passengers, daily_rate = car
        year_str = str(year) if year else "N/A"
        type_str = car_type or "N/A"
        color_str = color or "N/A"
        fuel_str = fuel or "N/A"
        pass_str = str(passengers) if passengers else "N/A"
        rate_str = f"${daily_rate:.0f}" if daily_rate else "N/A"
        print(
            f"{car_code:<12} {make:<12} {model:<15} {year_str:<6} {type_str:<12} {color_str:<8} {fuel_str:<8} {pass_str:<5} {rate_str:<8}")

    print()
    car = input("Enter car code (or press Enter to go back): ").strip()
    return car if car else None


def new_rental():
    print("\nNew rental form")
    car_code = list_available()

    if not car_code:
        return

    # Verify car exists and is available
    car = db.get_car_by_code(car_code)
    if not car:
        print("Invalid car code")
        return

    if not car[9]:  # is_available field (index 9 in the updated query)
        print("Car is not available")
        return

    customer_name = input("Enter customer name: ").strip()
    if not customer_name:
        print("Customer name is required")
        return

    success, message = db.rent_car(car_code, customer_name)
    print(f"\n{message}")


def new_return():
    print("\nReturn a car")
    car_code = input("Enter car code to return: ").strip()

    if not car_code:
        print("Car code is required")
        return

    success, message = db.return_car(car_code)
    print(f"\n{message}")


def help_menu():
    print("\nCommands and what they do:")
    print("list or ls - Show available cars")
    print("rent - Rent a car to a customer")
    print("return - Return a rented car")
    print("migrate - Import cars from CSV file")
    print("help - Show this help menu")
    print("exit - Quit the program\n")


# Main program
print()
print("Welcome to Global Car Rental Management System\n")

# Check if database has any cars
cars = db.get_available_cars()
if not cars:
    print("No cars found in database.")
    migrate_choice = input("Would you like to import cars from a CSV file? (y/n): ").lower()
    if migrate_choice == 'y':
        migrate_csv()

x = "0"
while x != "exit":
    x = input("\nlist, rent, return, migrate, help, or exit: ").lower()

    if x in ["list", "ls"]:
        list_available()
    elif x == "rent":
        new_rental()
    elif x == "return":
        new_return()
    elif x == "migrate":
        migrate_csv()
    elif x == "help":
        help_menu()
    elif x == "exit":
        break

print("Thank you for using Global Car Rental Management System!")