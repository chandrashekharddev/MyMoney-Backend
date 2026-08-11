import sqlite3
from langchain.tools import tool

DB_PATH = "database/expense.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# @tool
def create_table():
    """Create the expenses table in the database if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    q1 = """CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT
    );"""

    cursor.execute(q1)
    conn.commit()
    conn.close()

# Insert expense
@tool
def insert_expense(user_id: str, date: str, category: str, amount: float, description: str):
    """Insert a new expense into the expenses table."""
    conn = get_connection()
    cursor = conn.cursor()

    create_table()
    q2 = """INSERT INTO expenses (user_id, date, category, amount, description)
            VALUES (?, ?, ?, ?, ?);"""

    cursor.execute(q2, (user_id, date, category, amount, description))
    conn.commit()
    conn.close()


@tool
def fetch_expenses(user_id: str):
    """Fetch all expenses."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE user_id=?;",(user_id,))
    rows = cursor.fetchall()

    conn.close()
    return rows

# Fetch expenses by category
@tool
def fetch_expenses_by_category(user_id: str, category: str):
    """Fetch expenses by category.
    param category: Category of expenses to fetch"""
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE user_id=? AND category = ?;", (user_id, category))
    rows = cursor.fetchall()

    conn.close()
    return rows

# Fetch total expenses between dates 
@tool
def fetch_total_expenses_between_dates(user_id: str, start_date: str, end_date: str):
    """Fetch total expenses between two dates.
    param start_date: Start date in YYYY-MM-DD format
    param end_date: End date in YYYY-MM-DD format"""
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id=? AND date BETWEEN ? AND ?;",
        (user_id, start_date, end_date)
    )
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0.0

# Fetch expenses between dates 
@tool
def fetch_expenses_between_dates(user_id: str, start_date: str, end_date: str):
    """Fetch expenses between two dates.
    param start_date: Start date in YYYY-MM-DD format
    param end_date: End date in YYYY-MM-DD format"""
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=? AND date BETWEEN ? AND ?;",
        (user_id, start_date, end_date)
    )
    rows = cursor.fetchall()

    conn.close()
    return rows





if __name__ == "__main__":
    create_table()
