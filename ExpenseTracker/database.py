import sqlite3

class Database:
    def __init__(self, db_name="expenses.db"):
        self.db_name = db_name
        self.create_table()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            note TEXT,
            date TEXT NOT NULL
        )
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def add_expense(self, amount, category, note, date):
        query = "INSERT INTO expenses(amount, category, note, date) VALUES(?, ?, ?, ?)"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (amount, category, note, date))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding expense: {e}")
            return False

    def add_multiple_expenses(self, expenses):
        query = "INSERT INTO expenses(amount, category, note, date) VALUES(?, ?, ?, ?)"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, expenses)
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error importing expenses: {e}")
            return 0

    def get_all_expenses(self):
        query = "SELECT id, amount, category, note, date FROM expenses ORDER BY id DESC"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting expenses: {e}")
            return []

    def get_expense_by_id(self, expense_id):
        query = "SELECT * FROM expenses WHERE id=?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (expense_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting expense: {e}")
            return None

    def update_expense(self, expense_id, amount, category, note, date):
        query = "UPDATE expenses SET amount=?, category=?, note=?, date=? WHERE id=?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (amount, category, note, date, expense_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating expense: {e}")
            return False

    def delete_expense(self, expense_id):
        query = "DELETE FROM expenses WHERE id=?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (expense_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting expense: {e}")
            return False

    def search_by_category(self, category):
        query = "SELECT id, amount, category, note, date FROM expenses WHERE category LIKE ? ORDER BY date DESC"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, ('%' + category + '%',))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error searching category: {e}")
            return []

    def search_by_date(self, date):
        query = "SELECT id, amount, category, note, date FROM expenses WHERE date = ? ORDER BY id DESC"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (date,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error searching date: {e}")
            return []

    def get_category_summary(self):
        query = "SELECT category, SUM(amount) as total FROM expenses GROUP BY category ORDER BY total DESC"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting category summary: {e}")
            return []

    def get_monthly_summary(self):
        query = "SELECT strftime('%Y-%m', date) as month, SUM(amount) as total FROM expenses GROUP BY month ORDER BY month DESC"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting monthly summary: {e}")
            return []

    def get_yearly_summary(self):
        query = "SELECT strftime('%Y', date) as year, SUM(amount) as total FROM expenses GROUP BY year ORDER BY year DESC"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting yearly summary: {e}")
            return []

    def get_statistics(self):
        query = "SELECT SUM(amount), MAX(amount), MIN(amount), AVG(amount), COUNT(id) FROM expenses"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                row = cursor.fetchone()
                if row and row[0] is not None:
                    return {
                        "total": row[0],
                        "highest": row[1],
                        "lowest": row[2],
                        "average": row[3],
                        "count": row[4]
                    }
                return {"total": 0, "highest": 0, "lowest": 0, "average": 0, "count": 0}
        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")
            return {"total": 0, "highest": 0, "lowest": 0, "average": 0, "count": 0}
