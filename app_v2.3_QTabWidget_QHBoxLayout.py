import sys
from datetime import datetime
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTabWidget,
    QHBoxLayout,
    QTableView,
    QMessageBox,
)
from PySide6.QtGui import QDesktopServices, QAction
from PySide6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PySide6.QtWidgets import QAbstractItemView


# --- Database connection helper ---
def connect_to_sqlite_db(db_file):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_file)
    if not db.open():
        print(f"Error: Could not open database connection to {db_file}.")
        print(db.lastError().text())
        return None
    print(f"Successfully connected to {db_file}.")
    return db


# --- WhatsApp placeholder functions ---
def wa_cars_coming_today():
    print("Cars coming action triggered.")


def wa_return_car_procedure():
    car_mm = "Audi Q7"
    return_date = datetime.today().strftime("%d.%m")
    return_time = datetime.now().strftime("%H:%M")
    message = f"Hello, the {car_mm} is due to be returned on {return_date} at {return_time}."
    url_to_open = f"https://wa.me/995555211582?text={message}"
    success = QDesktopServices.openUrl(QUrl(url_to_open))
    if success:
        print(f"Successfully opened: {url_to_open}")
    else:
        print(f"Failed to open: {url_to_open}")


# --- Main window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Global Car Rental")
        self.setGeometry(200, 100, 1000, 600)

        # --- Database ---
        self.db = connect_to_sqlite_db("car_rental.db")
        if not self.db:
            QMessageBox.critical(self, "Database Error", "Failed to connect to database.")

        # --- Main model for All Cars ---
        self.model_all_cars = None
        if self.db:
            self.model_all_cars = QSqlTableModel(self, self.db)
            self.model_all_cars.setTable("cars")
            self.model_all_cars.select()

        # --- Central widget & layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Side tabs ---
        self.side_tabs = QTabWidget()
        # self.side_tabs.setFixedWidth(200)
        self.side_tabs.setTabPosition(QTabWidget.TabPosition.West)  # vertical tabs left

        # Tabs placeholders
        self.tab_all_cars = QWidget()
        self.tab_available_cars = QWidget()
        self.tab_rentals = QWidget()
        self.tab_returning_today = QWidget()

        self.side_tabs.addTab(self.tab_all_cars, "Master Inventory")
        self.side_tabs.addTab(self.tab_available_cars, "Available Cars")
        self.side_tabs.addTab(self.tab_rentals, "Rented Out")
        self.side_tabs.addTab(self.tab_returning_today, "Returning Soon")

        # --- Main table view ---
        self.table_view_all_cars = QTableView()
        if self.model_all_cars:
            self.table_view_all_cars.setModel(self.model_all_cars)
            self.table_view_all_cars.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.table_view_all_cars.resizeColumnsToContents()
            self.table_view_all_cars.verticalHeader().setVisible(False)

        # --- Add widgets to layout ---
        main_layout.addWidget(self.side_tabs)           # left tabs (static)
        main_layout.addWidget(self.table_view_all_cars) # main content table
        main_layout.setStretch(0, 0)  # tabs fixed
        main_layout.setStretch(1, 1)  # table expands

        # --- Menu bar ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        # Show Available Cars (copies to clipboard)
        action_ac = QAction("Available Cars- clipboard", self)
        action_ac.triggered.connect(self.show_available_cars)
        file_menu.addAction(action_ac)

        # WhatsApp actions
        action_cc = QAction("Cars Coming Today", self)
        action_cc.triggered.connect(wa_cars_coming_today)
        file_menu.addAction(action_cc)

        action_rcm = QAction("Return Car Message", self)
        action_rcm.triggered.connect(wa_return_car_procedure)
        file_menu.addAction(action_rcm)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)


    # --- Copy available cars to clipboard ---
    def show_available_cars(self):
        if not self.db or not self.db.isOpen():
            QMessageBox.warning(self, "Database Error", "Database connection is not open.")
            return

        query = QSqlQuery(self.db)
        if query.exec(
            """
            SELECT year, car_code, registration
            FROM cars
            WHERE is_available = 1
            ORDER BY car_code
            """
        ):
            results = []
            while query.next():
                year = query.value(0)
                car_code = query.value(1)
                registration = query.value(2)
                results.append(f"{year}\t{car_code}\t{registration}")

            if results:
                text = "\n\t".join(results)
                QApplication.clipboard().setText(f"Available cars:\n\t{text}")
                QMessageBox.information(self, "Copied", "All 'Available cars' are copied to the clipboard")
            else:
                QMessageBox.information(self, "No Results", "No available cars found.")
        else:
            QMessageBox.critical(self, "Query Failed", query.lastError().text())


# --- Run app ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
