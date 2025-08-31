import sys
from datetime import datetime
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtSql import QSqlDatabase, QSqlQuery

# GLOBAL VARIABLES


# DB CONNECTION LOGIC
def connect_to_sqlite_db(db_file):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_file)

    if not db.open():
        print(f"Error: Could not open database connection to {db_file}.")
        print(db.lastError().text())
        return None
    else:
        print(f"Successfully connected to {db_file}.")
        return db


def wa_cars_coming_today():
    # query the 'rentals' .db file for all cars coming in the next 24 hours
    # maybe keep a column to track if texted or not (return_reminder_sent = true) etc
    print("Cars coming action triggered.")
    print("This will query cars coming and export to whatsapp URL.")


def wa_return_car_procedure():
    # put into one string and send to whatsapp url via phone number, algorithmically
    # whatsapp API won't allow multi messages, must execute via loop or individually send via button

    car_mm = "Audi Q7" # car make & model query
    return_date = datetime.today().strftime("%d.%m") # return date query
    return_time = datetime.now().strftime("%H:%M") # return time query

    message = f"""
    Hello, the {car_mm} is due to be returned on {return_date} at {return_time}. Please:\b
    1. Arrive early to allow us to check the car\b
    2. Have car clean, petrol same as when taken\b
    3. Park in same parking lot (on right side)\b
"""

    # WhatsApp URL to open
    url_to_open = f"https://wa.me/995555211582?text={message}"

    # Create a QUrl object from the string URL
    q_url = QUrl(url_to_open)

    # Open the URL using QDesktopServices
    success = QDesktopServices.openUrl(q_url)

    if success:
        print(f"Successfully opened: {url_to_open}")
    else:
        print(f"Failed to open: {url_to_open}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Global Car Rental")
        self.setGeometry(300, 150, 800, 600)

        # Create the menu bar
        menu_bar = self.menuBar()

        # Add the 'File' menu
        file_menu = menu_bar.addMenu("&File")

        # Add actions to the 'File' menu
        # '&' before a letter creates a keyboard accelerator (Alt+F for File)

        # WHATSAPP CARS COMING TODAY
        action_cc = QAction("Cars Coming Today", self)
        file_menu.addAction(action_cc)
        action_cc.triggered.connect(wa_cars_coming_today)

        # WHATSAPP RETURN CAR MESSAGE
        action_rcm = QAction("Return Car Message", self)
        file_menu.addAction(action_rcm)
        action_rcm.triggered.connect(wa_return_car_procedure)

        # Add a separator line
        file_menu.addSeparator()

        # Add the 'Exit' action, connecting it to the app's quit function
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()


    # CONNECT TO DATABASE
    database_path = "car_rental.db"
    connection = connect_to_sqlite_db(database_path)

# THIS IS SQLITE LOGIC NEED WHILE LOOP TO PRINT QUERY in QSQLQuery
    if connection:
        query = QSqlQuery(connection)
        if query.exec('''
            SELECT car_code, make, model, year, daily_rate
            FROM cars
            WHERE is_available = TRUE
            ORDER BY make, model
        '''):
            while query.next():
                car_code = query.value(0)  # First column
                make = query.value(1)  # Second column
                model = query.value(2)  # Third column
                year = query.value(3)  # Fourth column
                daily_rate = query.value(4)  # Fifth column

                print(car_code, make, model, year, daily_rate)
        else:
            print("Query failed:", query.lastError().text())

        connection.close()  # Close the connection when done


    sys.exit(app.exec())