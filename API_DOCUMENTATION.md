# PolySportsLab API Documentation

## Overview

PolySportsLab is an AI-powered sports market analysis platform built on Polymarket's sports prediction markets. This API provides access to real-time smart money tracking, AI predictions, odds comparisons, and whale position analysis.

- **Base URL**: `https://polysportslab.com`
- **Authentication**: Telegram OAuth (Cookie-based)
- **Data Source**: Polymarket, ESPN, various sportsbooks

## Authentication

The API uses a cookie-based authentication system linked to Telegram accounts.

### 1. Obtaining Access
To access protected endpoints, you must have a valid `auth_session_v2` cookie.
1. Visit [PolySportsLab](https://polysportslab.com).
2. Log in via Telegram.
3. Extract the `auth_session_v2` cookie from your browser's developer tools.

### 2. Using the Cookie
Include the cookie in the `Cookie` header of your HTTP requests:
```http
Cookie: auth_session_v2=YOUR_COOKIE_VALUE_HERE
```

**Note**: The cookie value is a URL-encoded JSON string containing user details (ID, Telegram ID, role, etc.).

## Core Endpoints

### 1. Market List
Get a list of active markets with volume, liquidity, and price info.

- **Endpoint**: `GET /api/polymarket`
- **Parameters**:
  - `limit` (optional): Number of markets to return (default: 60)
  - `id` (optional): Fetch a specific market by ID

**Example Request**:
```bash
curl "https://polysportslab.com/api/polymarket?limit=10" \
  -H "Cookie: auth_session_v2=..."
```

**Response Structure**:
```json
[
  {
    "marketId": "1011429",
    "title": "76ers vs. Grizzlies",
    "volume": 342974.05,
    "liquidity": 100442.87,
    "prices": { "yes": 0.525, "no": 0.475 },
    "startTime": "2025-12-31 01:00:00+00"
  }
]
```

### 2. Whale Analysis (Market Holders)
Analyze the top holders ("whales") for a specific market condition.

- **Endpoint**: `GET /api/market-holders`
- **Parameters**:
  - `conditionId`: The unique condition ID of the market (obtainable from Market List)
  - `limit` (optional): Number of holders to return (default: 20)

**Example Request**:
```bash
curl "https://polysportslab.com/api/market-holders?conditionId=0x123...&limit=5" \
  -H "Cookie: auth_session_v2=..."
```

**Response Structure**:
```json
{
  "success": true,
  "data": {
    "whaleConcentration": 43.19,
    "smartMoneyDirection": "NEUTRAL",
    "yesHolders": [
      {
        "pseudonym": "timfish",
        "amount": 10000,
        "proxyWallet": "0x3eeb..."
      }
    ],
    "noHolders": [...]
  }
}
```

### 3. Smart Money Activity Feed
Get a real-time feed of smart money transactions (Buy, Sell, Redeem).

- **Endpoint**: `GET /api/smart-money`
- **Refresh Interval**: Recommended every 5 seconds

**Response Structure**:
```json
[
  {
    "type": "buy",
    "token": "🟢",
    "title": "Spread: Thunder (-17.5)",
    "amount": "500.00",
    "wallet": "Smart Money Bot",
    "status": "🌱 Open"
  }
]
```

### 4. AI Predictions
Get AI-generated probabilities and reasoning for markets.

- **Endpoint**: `POST /api/predictions/batch`
- **Body**:
```json
{
  "marketIds": ["1011429", "1011453"]
}
```

**Response**: Returns a map of market IDs to prediction objects containing `prob`, `confidence`, `reasoning`, and `keyFactors`.

### 5. Odds Comparison
Compare Polymarket odds with other sportsbooks (FanDuel, DraftKings, etc.).

- **Endpoint**: `GET /api/odds/compare`
- **Parameters**:
  - `marketId`: Market ID
  - `teamA`: Home team name
  - `teamB`: Away team name
  - `polyYes`: Current Polymarket YES price
  - `polyNo`: Current Polymarket NO price

## Rate Limiting & Best Practices

- **Rate Limits**: The API does not publish strict rate limits, but it is recommended to add delays (e.g., 0.5s) between requests to avoid IP bans.
- **Data Freshness**:
  - Smart Money: ~5s
  - Market Prices: ~30s
  - Whale Positions: ~30s
- **Timezones**: All timestamps are in UTC.

## Error Handling

Standard HTTP status codes are used:
- `200`: Success
- `401`: Unauthorized (Invalid or missing cookie)
- `404`: Resource not found
- `500`: Server error
