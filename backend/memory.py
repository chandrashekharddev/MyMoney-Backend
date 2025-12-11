import sqlite3
import os

# Get absolute path to database directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'memory.db')

# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_connection():
    """Create a new database connection for each request."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_memory_table():
    """Create the memory table in the database if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    q1 = """ CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            memory_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        ); """
    
    cursor.execute(q1)
    conn.commit()
    conn.close()  # IMPORTANT: Close connection after use

def insert_memory(user_id, role, memory_text):
    """Insert a new memory into the memory table."""
    # Create table if it doesn't exist
    create_memory_table()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    q2 = """ INSERT INTO memory (user_id, role, memory_text)
             VALUES (?, ?, ?); """
    cursor.execute(q2, (user_id, role, memory_text))
    conn.commit()
    conn.close()  # IMPORTANT: Close connection after use

def fetch_memories_by_user(user_id):
    """Fetch memories from the memory table by user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    
    q3 = "SELECT * FROM memory WHERE user_id = ? ORDER BY timestamp;"
    cursor.execute(q3, (user_id,))
    results = cursor.fetchall()
    
    conn.close()  # IMPORTANT: Close connection after use
    return results

def clear_memories_by_user(user_id):
    """Clear all memories from the memory table for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    q4 = "DELETE FROM memory WHERE user_id = ?;"
    cursor.execute(q4, (user_id,))
    conn.commit()
    conn.close()  # IMPORTANT: Close connection after use

if __name__ == "__main__":
    create_memory_table()
    print(f"Memory database initialized at: {DB_PATH}")