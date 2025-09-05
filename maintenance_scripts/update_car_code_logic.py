from PySide6.QtSql import QSqlDatabase, QSqlQuery


def connect_to_sqlite_db(db_file):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_file)
    if not db.open():
        print("Could not connect:", db.lastError().text())
        return None
    return db


def update_car_codes(db):
    query = QSqlQuery(db)
    if not query.exec("SELECT id, car_code, registration FROM cars"):
        print("Select failed:", query.lastError().text())
        return

    while query.next():
        car_id = query.value(0)
        car_code = query.value(1)
        registration = query.value(2)

        if not car_code or not registration:
            continue

        # Algorithm: chop car_code after 8 chars, append registration
        base = car_code[:8]
        new_code = f"{base}{registration}"

        update = QSqlQuery(db)
        update.prepare("UPDATE cars SET car_code = ? WHERE id = ?")
        update.addBindValue(new_code)
        update.addBindValue(car_id)

        if not update.exec():
            print(f"❌ Update failed for {car_id}: {update.lastError().text()}")
        else:
            print(f"✅ Updated {car_id}: {car_code} → {new_code}")


if __name__ == "__main__":
    print("🚗 Running maintenance: update_car_codes.py")
    db = connect_to_sqlite_db("../car_rental.db")  # adjust path if needed
    if db:
        update_car_codes(db)
        db.close()
        print("🎉 Done!")
