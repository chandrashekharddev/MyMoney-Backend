import sqlite3
import os
from langchain.tools import tool

# FIX: Use absolute path for Render compatibility
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'expense.db')

# FIX: Create database directory if it doesn't exist
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_connection():
    """Create a new database connection for each request."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Create table
def create_table():
    """Create the expenses table in the database if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    q1 = """CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,  # FIX: Changed from INTEGER to TEXT
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
    
    return f"Expense added: {description} - ₹{amount} on {date}"

# Fetch all expenses (non-tool version for internal use)
def fetch_expense(user_id):
    """Fetch all expenses."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE user_id=?;", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

@tool
def fetch_expenses(user_id):
    """Fetch all expenses."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE user_id=?;", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No expenses found."
    
    # Format the response
    result = "Your expenses:\n"
    for row in rows:
        result += f"- ₹{row[4]} on {row[2]} for {row[3]} ({row[5]})\n"
    return result

# Fetch expenses by category
@tool
def fetch_expenses_by_category(user_id, category):
    """Fetch expenses by category."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE user_id=? AND category=?;", (user_id, category))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return f"No expenses found in category: {category}"
    
    result = f"Expenses in {category}:\n"
    total = 0
    for row in rows:
        result += f"- ₹{row[4]} on {row[2]}: {row[5]}\n"
        total += row[4]
    result += f"\nTotal: ₹{total}"
    return result

# Fetch total expenses between dates 
@tool
def fetch_total_expenses_between_dates(user_id, start_date, end_date):
    """Fetch total expenses between two dates."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id=? AND date BETWEEN ? AND ?;",
        (user_id, start_date, end_date)
    )
    result = cursor.fetchone()
    conn.close()
    
    total = result[0] if result and result[0] else 0.0
    return f"Total expenses from {start_date} to {end_date}: ₹{total:.2f}"

# Fetch expenses between dates 
@tool
def fetch_expenses_between_dates(user_id, start_date, end_date):
    """Fetch expenses between two dates."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=? AND date BETWEEN ? AND ? ORDER BY date;",
        (user_id, start_date, end_date)
    )
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return f"No expenses found between {start_date} and {end_date}"
    
    result = f"Expenses from {start_date} to {end_date}:\n"
    total = 0
    for row in rows:
        result += f"- {row[2]}: ₹{row[4]} for {row[3]} ({row[5]})\n"
        total += row[4]
    result += f"\nTotal: ₹{total:.2f}"
    return result

# FIXED: Fetch highest expense day
@tool
def fetch_highest_expense_day(user_id):
    """Fetch the day with highest total expenses."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, SUM(amount) as daily_total 
        FROM expenses 
        WHERE user_id=? 
        GROUP BY date 
        ORDER BY daily_total DESC 
        LIMIT 1;
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] and row[1]:
        return f"Highest spending day: {row[0]} with ₹{row[1]:.2f}"
    return "No expenses found."

# FIXED: Edit expense function (corrected SQL and variable names)
@tool
def edit_expense(expense_id, amount=None, category=None, description=None):
    """Edit an existing expense."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build update query dynamically based on provided fields
    updates = []
    params = []
    
    if amount is not None:
        updates.append("amount = ?")
        params.append(amount)
    if category is not None:
        updates.append("category = ?")
        params.append(category)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    
    if not updates:
        conn.close()
        return "No changes specified."
    
    params.append(expense_id)
    query = f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?"
    
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    
    return f"Expense {expense_id} updated successfully."

# FIXED: Delete expense function
@tool
def delete_expense(user_id, expense_id=None, date=None):
    """Delete expenses by ID or date."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if expense_id:
        cursor.execute("DELETE FROM expenses WHERE user_id=? AND id=?;", (user_id, expense_id))
        message = f"Expense {expense_id} deleted."
    elif date:
        cursor.execute("DELETE FROM expenses WHERE user_id=? AND date=?;", (user_id, date))
        message = f"All expenses on {date} deleted."
    else:
        conn.close()
        return "Please provide either expense_id or date to delete."
    
    conn.commit()
    conn.close()
    return message

# Fetch daily spending data for visualizations
def fetch_daily_spending(user_id):
    """Fetch daily spending data."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, SUM(amount) as total_amount 
        FROM expenses 
        WHERE user_id=? 
        GROUP BY date 
        ORDER BY date;
    """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    create_table()
    print(f"Expense database initialized at: {DB_PATH}")