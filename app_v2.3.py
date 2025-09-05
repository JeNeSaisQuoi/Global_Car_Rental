import sys
from datetime import datetime

from PySide6 import QtWidgets
from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTabWidget,
    QHBoxLayout,
    QTableView,
    QMessageBox, QLineEdit, QWidgetAction, QMenu,
)
from PySide6.QtGui import QDesktopServices, QAction, QIcon, QKeySequence, QShortcut, QColor
from PySide6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PySide6.QtWidgets import QAbstractItemView


# --- Database connection checker ---
def connect_to_sqlite_db(db_file):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_file)
    if not db.open():
        print(f"Error: Could not open database connection to {db_file}.")
        print(db.lastError().text())
        return None
    print(f"Successfully connected to {db_file}.")
    return db


# --- WhatsApp functions ---
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

class MainWindow(QMainWindow):
    def __init__(self):
            super().__init__()
            self.setWindowTitle("Global Car Rental")
            self.setGeometry(200, 100, 1100, 650)

            # --- Database ---
            self.db = connect_to_sqlite_db("car_rental.db")
            if not self.db:
                QMessageBox.critical(self, "Database Error", "Failed to connect to database.")

            # --- Menu Bar ---
            menu_bar = self.menuBar()
            file_menu = menu_bar.addMenu("&File")

            # --- SEARCH TOOLBAR with a QLineEdit ---
            toolbar = self.addToolBar("Main Toolbar")
            toolbar.setMovable(False)  # keep it static

            self.search_box = QLineEdit()
            self.search_box.setPlaceholderText("Search cars...")
            self.search_box.setFixedWidth(200)

            toolbar.addWidget(self.search_box)
            toolbar.addSeparator()

            action_ac = QAction("Available Cars - clipboard", self)
            action_ac.triggered.connect(self.clipboard_avail_cars)
            file_menu.addAction(action_ac)

            action_cc = QAction("Cars Coming Today", self)
            action_cc.triggered.connect(wa_cars_coming_today)
            file_menu.addAction(action_cc)

            action_rcm = QAction("Return Car Message", self)
            action_rcm.triggered.connect(wa_return_car_procedure)
            file_menu.addAction(action_rcm)

            file_menu.addSeparator()

            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)


            # --- Central widget & layout ---
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QHBoxLayout(central_widget)

            # --- Side tabs ---
            self.side_tabs = QTabWidget()
            self.side_tabs.setTabPosition(QTabWidget.TabPosition.West)  # vertical tabs on the left
            main_layout.addWidget(self.side_tabs)

            # Shortcut for cycling tabs forward
            shortcut_next_tab = QShortcut(QKeySequence("Ctrl+Tab"), self)
            shortcut_next_tab.setContext(Qt.ShortcutContext.ApplicationShortcut)
            shortcut_next_tab.activated.connect(self.cycle_tabs)

            # Tabs
            self.tab_all_cars = QWidget()
            self.tab_available_cars = QWidget()
            self.tab_rentals = QWidget()
            self.tab_returning_today = QWidget()

            self.side_tabs.addTab(self.tab_all_cars, "Master Inventory")
            self.side_tabs.addTab(self.tab_available_cars, "Available Cars")
            self.side_tabs.addTab(self.tab_rentals, "Rented Out")
            self.side_tabs.addTab(self.tab_returning_today, "Returning Soon")

            # --- Master Inventory (all cars) ---
            if self.db:
                self.model_all_cars = QSqlTableModel(self, self.db)
                self.model_all_cars.setTable("cars")
                self.model_all_cars.select()

                self.table_view_all_cars = QTableView()
                self.table_view_all_cars.setModel(self.model_all_cars)
                self.table_view_all_cars.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                self.table_view_all_cars.resizeColumnsToContents()
                self.table_view_all_cars.verticalHeader().setVisible(False)

                layout_all = QHBoxLayout(self.tab_all_cars)
                layout_all.addWidget(self.table_view_all_cars)

            # --- Available Cars ---
            if self.db:
                self.model_available_cars = QSqlTableModel(self, self.db)
                self.model_available_cars.setTable("cars")
                self.model_available_cars.setFilter("is_available = 1") # .setFilter used to filter db
                self.model_available_cars.setSort(1, Qt.SortOrder.AscendingOrder)  # default hard-code sort by column index 1
                self.model_available_cars.select()

                self.table_view_available_cars = QTableView()
                self.table_view_available_cars.setModel(self.model_available_cars)
                self.table_view_available_cars.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                self.table_view_available_cars.resizeColumnsToContents()
                self.table_view_available_cars.verticalHeader().setVisible(False)
                # --- Enable interactive sorting by clicking headers ---
                self.table_view_available_cars.setSortingEnabled(True)

                layout_avail = QHBoxLayout(self.tab_available_cars)
                layout_avail.addWidget(self.table_view_available_cars)


    def cycle_tabs(self):
        current = self.side_tabs.currentIndex()
        count = self.side_tabs.count()
        self.side_tabs.setCurrentIndex((current + 1) % count)

    # --- Copy available cars to clipboard ---
    def clipboard_avail_cars(self):
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
                QMessageBox.information(self, "Copied", "'Available cars' was copied to clipboard")
            else:
                QMessageBox.information(self, "No Results", "No available cars found.")
        else:
            QMessageBox.critical(self, "Query Failed", query.lastError().text())


# --- Run app ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon = QIcon("icon/icon1.ico")
    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec())