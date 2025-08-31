import sys
from datetime import datetime
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery


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


        # --- DATABASE CONNECTION ---
        self.db = connect_to_sqlite_db("car_rental.db")
        if not self.db:
            QMessageBox.critical(self, "Database Error", "Failed to connect to database.")


        # --- MENU BAR ITEMS ---
        menu_bar = self.menuBar()
        # FILE -- main menu
        file_menu = menu_bar.addMenu("&File")
        # ACTIONS inside FILE MENU

        # AVAILABLE CARS menu item
        # for easy copy/paste to the Tbilisi group
        action_ac = QAction("Show Available Cars", self)
        file_menu.addAction(action_ac)
        action_ac.triggered.connect(self.show_available_cars)

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

        # --- DB connection for the TABLE VIEW ---
        self.db = connect_to_sqlite_db("car_rental.db")

        if self.db:
            # Model for the 'cars' table
            self.model = QSqlTableModel(self, self.db)
            self.model.setTable("cars")
            # self.model.setEditStrategy(QSqlTableModel.OnFieldChange)  # optional: makes table editable
            self.model.select()

            # Table view widget
            self.table_view = QTableView()
            self.table_view.setModel(self.model)
            self.table_view.resizeColumnsToContents()

            # Layout container
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.addWidget(self.table_view)
            self.setCentralWidget(container)


    # SHOW AVAILABLE IN A DIALOG BOX
    def show_available_cars(self):
        if not self.db.isOpen():
            QMessageBox.warning(self, "Database Error", "Database connection is not open.")
            return

        query = QSqlQuery(self.db)
        if query.exec("""
            SELECT year, make, model, registration
            FROM cars
            WHERE is_available = TRUE
            ORDER BY make, model
        """):
            results = []
            while query.next():
                year = query.value(0)
                make = query.value(1)
                model = query.value(2)
                registration = query.value(3)
                results.append(f"{year}: {make} {model} ({registration}")

            if results:
                msg = "\n".join(results)
            else:
                msg = "No available cars found."

            QMessageBox.information(self, "Available Cars:", msg)
        else:
            QMessageBox.critical(self, "Query Failed", query.lastError().text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())