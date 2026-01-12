import sqlite3
import os

DB_FILE = "market_history.db"

def init_db():
    """Initialize the SQLite database with the required table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create table for market history
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_id TEXT NOT NULL,
        market_title TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        volume REAL,
        liquidity REAL,
        price_yes REAL,
        price_no REAL,
        whale_concentration REAL,
        smart_money_direction TEXT,
        top10_concentration REAL
    )
    """)
    
    # Create index for faster querying by market_id and timestamp
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_timestamp ON market_history (market_id, timestamp)")
    
    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_FILE}")

if __name__ == "__main__":
    init_db()
