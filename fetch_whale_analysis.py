import requests
import json
import time
from datetime import datetime
import os
import concurrent.futures
from urllib.parse import unquote

# Try to import dotenv, but fallback to manual parsing if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Manual .env parser
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

import sqlite3

# Configuration
BASE_URL = "https://polysportslab.com"
AUTH_COOKIE_RAW = os.environ.get("auth_session_v2", "")
DB_FILE = "market_history.db"


# Configuration (Restored)
if not AUTH_COOKIE_RAW:
    print("WARNING: 'auth_session_v2' not found in environment variables or .env file.")
    print("Please check your .env file.")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": f"auth_session_v2={AUTH_COOKIE_RAW}",
    "Accept-Encoding": "gzip, deflate"
}

OUTPUT_MD = "market_whale_analysis.md"
OUTPUT_JSON = "market_whale_analysis.json"
MAX_WORKERS = 5  # Number of concurrent requests

def get_top_markets(limit=20):
    """Fetch the top markets from the API."""
    url = f"{BASE_URL}/api/polymarket"
    params = {"limit": limit}
    
    try:
        print(f"Fetching top {limit} markets...")
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error decoding JSON: {e}")
        print(f"Response status: {response.status_code}")
        print(f"Response text preview: {response.text[:500]}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching markets: {e}")
        if 'response' in locals():
             print(f"Response text preview: {response.text[:500]}")
        return []

def get_market_holders(market):
    """Fetch holder analysis for a specific market condition."""
    condition_id = market.get('conditionId')
    if not condition_id:
        return None

    url = f"{BASE_URL}/api/market-holders"
    params = {
        "conditionId": condition_id,
        "limit": 20
    }
    
    try:
        # No sleep needed here if we rely on concurrency limits, but a small delay helps avoid burst limits
        # time.sleep(0.1) 
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        if response.status_code == 429:
            print(f"Rate limited on {market.get('title')}. Retrying...")
            time.sleep(2)
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            
        response.raise_for_status()
        holders_data = response.json()
        
        return {
            "market": market,
            "holders": holders_data
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching holders for {market.get('title')}: {e}")
        return {
            "market": market,
            "holders": {"success": False, "error": str(e)}
        }

def format_currency(value):
    """Helper to format currency values."""
    if value is None:
        return "N/A"
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)

def format_percentage(value):
    """Helper to format percentage values."""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return str(value)

def save_to_db(analyzed_data):
    """Save analysis results to SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        for item in analyzed_data:
            market = item['market']
            holders = item['holders']
            
            # Extract basic market data
            market_id = market.get('marketId') or market.get('id')
            market_title = market.get('title')
            volume = market.get('volume')
            liquidity = market.get('liquidity')
            prices = market.get('prices', {})
            price_yes = prices.get('yes')
            price_no = prices.get('no')
            
            # Extract whale analysis data
            whale_conc = None
            smart_money_dir = None
            top10_conc = None
            
            if holders and holders.get('success'):
                data = holders.get('data', {})
                whale_conc = data.get('whaleConcentration')
                smart_money_dir = data.get('smartMoneyDirection')
                top10_conc = data.get('top10Concentration')
                
            cursor.execute("""
            INSERT INTO market_history (
                market_id, market_title, timestamp, volume, liquidity, 
                price_yes, price_no, whale_concentration, 
                smart_money_direction, top10_concentration
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                market_id, market_title, timestamp, volume, liquidity,
                price_yes, price_no, whale_conc,
                smart_money_dir, top10_conc
            ))
            
        conn.commit()
        conn.close()
        print(f"Saved {len(analyzed_data)} records to database.")
    except Exception as e:
        print(f"Error saving to database: {e}")

def generate_markdown(analyzed_data):
    """Generate the Markdown content."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_lines = [
        "# PolySportsLab Market Whale Analysis",
        f"*Generated on: {timestamp}*",
        "",
        "## Summary",
        f"- **Total Markets Analyzed**: {len(analyzed_data)}",
        "",
        "---",
        ""
    ]

    for index, item in enumerate(analyzed_data, 1):
        market = item['market']
        holders = item['holders']
        
        # Market Header
        title = market.get('title', 'Unknown Market')
        vol = format_currency(market.get('volume', 0))
        liq = format_currency(market.get('liquidity', 0))
        
        md_lines.append(f"## {index}. {title}")
        md_lines.append(f"- **Volume**: {vol} | **Liquidity**: {liq}")
        
        prices = market.get('prices', {})
        p_yes = prices.get('yes', 'N/A')
        p_no = prices.get('no', 'N/A')
        md_lines.append(f"- **Prices**: Yes: {p_yes} | No: {p_no}")
        
        if holders and holders.get('success'):
            data = holders.get('data', {})
            conc = format_percentage(data.get('whaleConcentration'))
            direction = data.get('smartMoneyDirection', 'N/A')
            
            md_lines.append(f"- **Whale Concentration**: {conc}")
            md_lines.append(f"- **Smart Money Direction**: {direction}")
            
            # Yes Holders Table
            md_lines.append("")
            md_lines.append("### 🟢 Top Holders (Yes)")
            yes_holders = data.get('yesHolders', [])
            if yes_holders:
                md_lines.append("| Rank | Holder | Amount |")
                md_lines.append("|------|--------|--------|")
                for i, h in enumerate(yes_holders[:5], 1): # Top 5 for brevity
                    name = h.get('pseudonym') or h.get('proxyWallet', 'Unknown')[:8]
                    amt = format_currency(h.get('amount', 0))
                    md_lines.append(f"| {i} | {name} | {amt} |")
            else:
                md_lines.append("No data available.")

            # No Holders Table
            md_lines.append("")
            md_lines.append("### 🔴 Top Holders (No)")
            no_holders = data.get('noHolders', [])
            if no_holders:
                md_lines.append("| Rank | Holder | Amount |")
                md_lines.append("|------|--------|--------|")
                for i, h in enumerate(no_holders[:5], 1):
                    name = h.get('pseudonym') or h.get('proxyWallet', 'Unknown')[:8]
                    amt = format_currency(h.get('amount', 0))
                    md_lines.append(f"| {i} | {name} | {amt} |")
            else:
                md_lines.append("No data available.")
                
        else:
            error_msg = holders.get('error', 'Unknown error') if holders else 'No data'
            md_lines.append(f"- *Whale data unavailable: {error_msg}*")
            
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    return "\n".join(md_lines)

def main():
    print("Starting Optimized Market Whale Analysis Script...")
    
    # 1. Fetch Markets
    markets = get_top_markets(limit=20)
    if not markets:
        print("No markets found. Exiting.")
        return

    print(f"Found {len(markets)} markets. Fetching whale analysis concurrently...")
    
    analyzed_data = []
    
    # 2. Process each market concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_market = {executor.submit(get_market_holders, market): market for market in markets}
        
        completed_count = 0
        total_count = len(markets)
        
        for future in concurrent.futures.as_completed(future_to_market):
            completed_count += 1
            print(f"[{completed_count}/{total_count}] Fetching completed...")
            result = future.result()
            if result:
                analyzed_data.append(result)

    # Sort results to maintain order (concurrency might shuffle them)
    # We can't easily sort by original index unless we stored it, but sorting by volume is a good default
    analyzed_data.sort(key=lambda x: x['market'].get('volume', 0), reverse=True)

    # 3. Generate Reports
    print("Generating reports...")
    
    # Save to DB
    print("Saving to database...")
    save_to_db(analyzed_data)

    # Save JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(analyzed_data, f, indent=2, ensure_ascii=False)
    print(f"JSON data saved to {OUTPUT_JSON}")

    # Save Markdown
    markdown_content = generate_markdown(analyzed_data)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Markdown report saved to {OUTPUT_MD}")
        
    print("All tasks completed successfully!")

if __name__ == "__main__":
    main()
