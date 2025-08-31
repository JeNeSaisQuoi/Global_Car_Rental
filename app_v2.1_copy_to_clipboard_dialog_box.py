import sys
from datetime import datetime
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableView,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery


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
    print("Cars coming action triggered.")
    print("This will query cars coming and export to whatsapp URL.")


def wa_return_car_procedure():
    car_mm = "Audi Q7"
    return_date = datetime.today().strftime("%d.%m")
    return_time = datetime.now().strftime("%H:%M")

    message = f"""
    Hello, the {car_mm} is due to be returned on {return_date} at {return_time}. Please:\b
    1. Arrive early to allow us to check the car\b
    2. Have car clean, petrol same as when taken\b
    3. Park in same parking lot (on right side)\b
"""

    url_to_open = f"https://wa.me/995555211582?text={message}"
    q_url = QUrl(url_to_open)
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


        # --- SINGLE DATABASE CONNECTION (created once) ---
        self.db = connect_to_sqlite_db("car_rental.db")
        if not self.db:
            QMessageBox.critical(self, "Database Error", "Failed to connect to database.")


        # --- MENU BAR ITEMS ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        # AVAILABLE CARS (copies available cars to clipboard)
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

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # --- DB model + main table view (shows full 'cars' table in main window) ---
        if self.db:
            self.model = QSqlTableModel(self, self.db)
            self.model.setTable("cars")
            # self.model.setEditStrategy(QSqlTableModel.OnFieldChange)  # optional
            self.model.select()

            self.table_view = QTableView()
            self.table_view.setModel(self.model)
            self.table_view.resizeColumnsToContents()

            container = QWidget()
            layout = QVBoxLayout(container)
            layout.addWidget(self.table_view)
            self.setCentralWidget(container)


    # SHOW AVAILABLE CARS w/ DIALOG BOX 'Copied to clipboard'
    def show_available_cars(self):
        # Make sure DB exists and is open
        if not self.db or not self.db.isOpen():
            QMessageBox.warning(self, "Database Error", "Database connection is not open.")
            return

        query = QSqlQuery(self.db)
        # Use 1 (integer) for SQLite boolean checks
        if query.exec(
            """
            SELECT year, make, model, registration
            FROM cars
            WHERE is_available = 1
            ORDER BY make, model
            """
        ):
            results = []
            while query.next():
                year = query.value(0)
                make = query.value(1)
                model = query.value(2)
                registration = query.value(3)
                # append each to one string
                results.append(f"{year} {make} {model} {registration}")

            if results:
                text = "\n".join(results)

                # COPY to clipboard
                QApplication.clipboard().setText(f"Available cars:\n{text}")

                # simple confirmation dialog box popup
                QMessageBox.information(self, "Copied", "Copied 'Available Cars' to clipboard")
            else:
                QMessageBox.information(self, "No Results", "No available cars found.")
        else:
            QMessageBox.critical(self, "Query Failed", query.lastError().text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())