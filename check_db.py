import sqlite3
import pandas as pd

DB_FILE = "market_history.db"

def query_history():
    """Query and display the last 5 records from the database."""
    conn = sqlite3.connect(DB_FILE)
    
    query = """
    SELECT market_title, timestamp, volume, whale_concentration, smart_money_direction 
    FROM market_history 
    ORDER BY timestamp DESC 
    LIMIT 5
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        print("Latest Market History Records:")
        print(df.to_string(index=False))
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    query_history()
