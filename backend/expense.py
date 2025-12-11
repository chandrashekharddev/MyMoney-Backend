import sqlite3
from langchain.tools import tool

DB_PATH = "database/expense.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Create table
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
def insert_expense(user_id, date, category, amount, description):
    """Insert a new expense into the expenses table."""
    conn = get_connection()
    cursor = conn.cursor()

    create_table()
    q2 = """INSERT INTO expenses (user_id, date, category, amount, description)
            VALUES (?, ?, ?, ?, ?);"""

    cursor.execute(q2, (user_id, date, category, amount, description))
    conn.commit()
    conn.close()

# Fetch all expenses
def fetch_expense(user_id):
    """Fetch all expenses."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE user_id=?;",(user_id,))
    rows = cursor.fetchall()

    conn.close()
    return rows


@tool
def fetch_expenses(user_id):
    """Fetch all expenses."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE user_id=?;",(user_id,))
    rows = cursor.fetchall()

    conn.close()
    return rows

# Fetch expenses by category
@tool
def fetch_expenses_by_category(user_id, category):
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
def fetch_total_expenses_between_dates(user_id, start_date, end_date):
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
def fetch_expenses_between_dates(user_id,start_date, end_date):
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

# Fetch highest expense - Optional Enhancement
@tool
def fetch_highest_expense_day(user_id):
    """Fetch the highest expense recorded."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT date,Sum(amount) FROM expenses WHERE id=? GROUP BY date ORDER BY amount DESC LIMIT 1;",(user_id,))
    row = cursor.fetchone()

    conn.close()
    return row

# Edit expense - Optional Enhancement
@tool
def edit_expense(user_id, amount=None, category=None, description=None):
    """Edit an existing expense.
    param id: ID of the expense to edit
    param amount: New amount (optional)
    param category: New category (optional)
    param description: New description (optional)
    """
    
    conn = get_connection()
    cursor = conn.cursor()
    cur.execute("""
        UPDATE expenses 
        SET amount=?, category=?, description=? 
        WHERE user_id=? 
    """, (amount, category, description, id))
    conn.commit()
    conn.close()
    
# Delete expense - Optional Enhancement
@tool
def delete_expense(user_id,date:None):
    """Delete an expense by ID.
    param id: ID of the expense to delete
    param date: Date of the expense to delete (optional)
    """
    conn = get_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("DELETE FROM expenses WHERE user_id=? AND date=? ;", (user_id,date))
    else:
        cursor.execute("DELETE FROM expenses WHERE user_id=? ;", (user_id,))
    conn.commit()
    conn.close()
    
#   ===============================================
#   Fuctions to retrive the data for visualizations
#   ===============================================

# Fetch daily spending data
def fetch_daily_spending(user_id):
    """Fetch daily spending data."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT date, SUM(amount) as total_amount FROM expenses WHERE id=? GROUP BY date ORDER BY date;",(user_id,))
    rows = cursor.fetchall()

    conn.close()
    return rows





if __name__ == "__main__":
    create_table()
    
    
    