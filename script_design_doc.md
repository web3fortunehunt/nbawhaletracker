# Market Analysis Script - Technical Implementation Document

## 1. Overview
This document outlines the technical design for a Python script intended to fetch data for the top 20 sports markets from PolySportsLab and generate a detailed "Whale Analysis" report in Markdown format.

## 2. Technical Stack
- **Language**: Python 3.x
- **Libraries**:
  - `requests`: For handling HTTP requests.
  - `json`: For parsing API responses.
  - `time`: For implementing rate limiting.
  - `datetime`: For timestamping the report.

## 3. API Integration Strategy

### 3.1 Base Configuration
- **Base URL**: `https://polysportslab.com`
- **Headers**:
  - `User-Agent`: Standard browser user agent to avoid bot detection.
  - `Cookie`: `auth_session_v2` (Required for accessing detailed whale/holder data if protected).

### 3.2 Endpoints

#### A. Fetch Top 20 Markets
- **Endpoint**: `GET /api/polymarket`
- **Parameters**: `limit=20`
- **Purpose**: Retrieve the list of top active markets.
- **Key Data to Extract**:
  - `marketId`: For reference.
  - `conditionId`: Required to fetch holders.
  - `title`: Market name (e.g., "Lakers vs Warriors").
  - `volume`: Total trading volume.
  - `liquidity`: Market liquidity.
  - `prices`: Current Yes/No prices.

#### B. Fetch Market Holders (Whale Analysis)
- **Endpoint**: `GET /api/market-holders`
- **Parameters**: 
  - `conditionId`: From the market list data.
  - `limit`: `20` (default).
- **Purpose**: Analyze top holders for each market.
- **Key Data to Extract**:
  - `yesHolders`: List of top holders for "Yes" outcome.
  - `noHolders`: List of top holders for "No" outcome.
  - `whaleConcentration`: Percentage of supply held by top holders.
  - `smartMoneyDirection`: Indicator of smart money sentiment.

## 4. Data Processing Flow

1.  **Initialization**: Setup session headers and load authentication cookie.
2.  **Fetch Markets**: 
    - Call `/api/polymarket?limit=20`.
    - Validate response status (200 OK).
    - Parse JSON list.
3.  **Iterate & Enrich**:
    - For each market in the list:
        - Extract `conditionId`.
        - **Delay**: Sleep for 1 second to respect rate limits.
        - Call `/api/market-holders`.
        - Merge holder data with market data.
4.  **Report Generation**:
    - Create a file `market_whale_analysis.md`.
    - Write header with generation timestamp.
    - Format each market section.

## 5. Output Format (Markdown)

The output file will follow this structure:

```markdown
# PolySportsLab Market Whale Analysis
*Generated on: YYYY-MM-DD HH:MM:SS*

## 1. [Market Title] (Vol: $XXX, Liq: $XXX)
- **Prices**: Yes: 0.XX | No: 0.XX
- **Whale Concentration**: XX.XX%
- **Smart Money Direction**: NEUTRAL/BULLISH/BEARISH

### Top Holders (Yes)
| Rank | Holder | Amount |
|------|--------|--------|
| 1    | name   | $1000  |

### Top Holders (No)
| Rank | Holder | Amount |
|------|--------|--------|
| 1    | name   | $1000  |

---
```

## 6. Error Handling
- **Network Errors**: Try-except blocks around request calls.
- **Rate Limiting**: Implementation of `time.sleep(1)` between calls to prevent 429 errors.
- **Empty Data**: Handle cases where no holders are returned gracefully (display "No data available").

## 7. Security Considerations
- The `auth_session_v2` cookie contains sensitive session data. It should be loaded from an environment variable or a separate config file (e.g., `.env`), not hardcoded in the script.

## 8. Proposed Script Structure

```python
import requests
import time
import json

class PolyMarketAnalyzer:
    def __init__(self, auth_cookie):
        self.base_url = "https://polysportslab.com"
        self.headers = {
            "Cookie": f"auth_session_v2={auth_cookie}",
            "User-Agent": "Mozilla/5.0 ..."
        }

    def get_top_markets(self, limit=20):
        # Implementation
        pass

    def get_market_holders(self, condition_id):
        # Implementation
        pass

    def generate_report(self, data):
        # Implementation
        pass

    def run(self):
        # Main execution loop
        pass
```
