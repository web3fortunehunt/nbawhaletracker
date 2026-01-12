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
);

-- Index for efficient querying by market and time
CREATE INDEX IF NOT EXISTS idx_market_timestamp ON market_history (market_id, timestamp);
