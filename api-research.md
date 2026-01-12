# PolySportsLab API Research Documentation

## Overview

PolySportsLab is an AI-powered sports market analysis platform built on Polymarket's sports prediction markets. The platform provides real-time smart money tracking, AI predictions, multi-platform odds comparison, and whale position analysis.

**Base URL**: `https://polysportslab.com`
**Tech Stack**: Next.js (frontend), Cloudflare (CDN/deployment)
**Authentication**: Telegram OAuth with cookie-based sessions

---

## API Endpoints

### 1. Smart Money Activity

**Endpoint**: `GET /api/smart-money`

**Description**: Real-time smart money trading activity feed

**Response Example**:
```json
[
  {
    "id": "f0cb8937-3829-4ba6-bdd9-c47f30fb4495",
    "type": "redeem",
    "token": "🟡",
    "title": "Spread: Thunder (-17.5)",
    "price": "N/A",
    "amount": "500.00",
    "time": "14:20:15",
    "url": "https://polymarket.com/event/...",
    "timestamp": 1767075615,
    "wallet": "聪明 15号",
    "outcome": "",
    "status": "💰 赎回 (Redeem)",
    "performance": {
      "win_rate": 90,
      "wins": 27,
      "losses": 3,
      "total_closed": 30,
      "active_positions": 500,
      "unrealized_pnl": 72.94,
      "total_redeemed": 23856.2
    }
  }
]
```

**Transaction Types**:
| Type | Token | Status |
|------|-------|--------|
| buy | 🟢 | 🌱 建仓 (Open) / 🔥 加仓 (Add) |
| sell | 🔴 | ✂️ 减仓 (Trim) / 💎 清仓 (Close) |
| redeem | 🟡 | 💰 赎回 (Redeem) |

---

### 2. Market List

**Endpoint**: `GET /api/polymarket?limit={limit}`

**Description**: Get list of all markets with basic info

**Parameters**:
- `limit` (optional): Number of markets to return (default: 60)

**Response Example**:
```json
[
  {
    "marketId": "1011429",
    "eventId": "1011429",
    "conditionId": "0x1f3c1702f93a90ce445c3854eb1ee74f8ae468a024a6c85a76afa597f40e8878",
    "eventSlug": "nba-phi-mem-2025-12-30",
    "marketSlug": "nba-phi-mem-2025-12-30",
    "title": "76ers vs. Grizzlies",
    "sport": "NBA",
    "startTime": "2025-12-31 01:00:00+00",
    "volume": 342974.054578,
    "liquidity": 100442.8749,
    "prices": {
      "yes": 0.525,
      "no": 0.475
    },
    "teamA": { "name": "Philadelphia 76ers" },
    "teamB": { "name": "Memphis Grizzlies" }
  }
]
```

---

### 3. Single Market Details

**Endpoint**: `GET /api/polymarket?id={marketId}`

**Description**: Get detailed info for a single market

**Parameters**:
- `id`: Market ID

**Response**: Same structure as market list item

---

### 4. AI Predictions (Batch)

**Endpoint**: `POST /api/predictions/batch`

**Description**: Get AI predictions for multiple markets

**Request Body**:
```json
{
  "marketIds": ["1011429", "1011453"]
}
```

**Response Example**:
```json
{
  "1011429": {
    "prob": 0.33,
    "isAISelected": false,
    "edge": 0,
    "side": null,
    "reasoning": ["Analysis text..."],
    "confidence": 0.874,
    "aiConfidence": "medium",
    "keyFactors": [
      "📋 伤病因素：...",
      "🏠 主场优势：...",
      "📈 近期状态：...",
      "⚔️ 交锋历史：...",
      "📅 赛程因素：...",
      "🎯 关键对位：...",
      "📊 趋势指标：..."
    ],
    "marketComparison": "My prediction vs market...",
    "diffReason": "Difference from XGBoost model..."
  }
}
```

---

### 5. Market Holders (Whale Analysis)

**Endpoint**: `GET /api/market-holders?conditionId={id}&limit={limit}`

**Description**: Get top holders for a market (whale positions)

**Parameters**:
- `conditionId`: Market condition ID (hex string)
- `limit`: Number of holders to return (default: 20)

**Response Example**:
```json
{
  "success": true,
  "data": {
    "yesHolders": [
      {
        "proxyWallet": "0x3eeb...c387",
        "amount": 10000,
        "outcomeIndex": 0,
        "pseudonym": "timfish",
        "profileImage": "https://..."
      }
    ],
    "noHolders": [...],
    "yesTotalAmount": 82916.238337,
    "noTotalAmount": 91145.299477,
    "whaleConcentration": 43.19,
    "smartMoneyDirection": "NEUTRAL",
    "top10Concentration": 80.59
  },
  "timestamp": 1767084929529
}
```

---

### 6. Smart Money Positions

**Endpoint**: `GET /api/smart-money/positions?slug={slug}&conditionId={id}&teamA={team}`

**Description**: Get smart money positions for a specific market

**Parameters**:
- `slug`: Market slug (e.g., "nba-phi-mem-2025-12-30")
- `conditionId`: Market condition ID
- `teamA`: Team A name (URL encoded)

**Response Example**:
```json
{
  "positions": {
    "yes": [
      {
        "label": "机器人",
        "address": "0xff12...",
        "outcome": "76ERS",
        "size": 5,
        "avgPrice": 0.54,
        "curPrice": 0.525,
        "currentValue": 2.625,
        "pnl": -0.075
      }
    ],
    "no": [...]
  },
  "total": 2,
  "yesTotal": 2.625,
  "noTotal": 2.375,
  "timestamp": 1767084929296
}
```

---

### 7. Odds History

**Endpoint**: `GET /api/odds/history?marketId={id}&hours={hours}&teamA={}&teamB={}&polyYes={}&polyNo={}`

**Description**: Historical odds data for charting

**Parameters**:
- `marketId`: Market ID
- `hours`: Time range (1, 6, 24)
- `teamA`, `teamB`: Team names
- `polyYes`, `polyNo`: Current Polymarket prices

**Response Example**:
```json
{
  "marketId": "1011429",
  "hours": 24,
  "dataPoints": 710,
  "history": [
    {
      "time": "16:56",
      "timestamp": 1766998569765,
      "polymarket_yes": 0.51,
      "polymarket_no": 0.49
    }
  ]
}
```

---

### 8. Multi-Platform Odds Comparison

**Endpoint**: `GET /api/odds/compare?marketId={id}&teamA={}&teamB={}&polyYes={}&polyNo={}`

**Description**: Compare odds across multiple sportsbooks

**Parameters**:
- `marketId`: Market ID
- `teamA`, `teamB`: Team names
- `polyYes`, `polyNo`: Current Polymarket prices

**Response Example**:
```json
{
  "marketId": "1011429",
  "teamA": "Philadelphia 76ers",
  "teamB": "Memphis Grizzlies",
  "comparison": [
    {
      "source": "polymarket",
      "sourceName": "Polymarket",
      "teamA": { "odds": 0.525, "implied": 52.5, "display": "52.5%" },
      "teamB": { "odds": 0.475, "implied": 47.5, "display": "47.5%" },
      "margin": 0,
      "lastUpdate": "2025-12-30T08:55:29.307Z"
    },
    {
      "source": "fanduel",
      "sourceName": "FanDuel",
      "teamA": { "odds": 1.847, "implied": 54.12, "display": "-118" },
      "teamB": { "odds": 2, "implied": 50, "display": "+100" },
      "margin": 4.12,
      "lastUpdate": "..."
    }
  ],
  "bestOdds": {
    "teamA": { "source": "rebet", "odds": 1.877 },
    "teamB": { "source": "ballybet", "odds": 2.02 }
  },
  "arbitrage": { "exists": false },
  "timestamp": 1767084929307
}
```

**Supported Platforms**:
- Polymarket, FanDuel, DraftKings, Caesars, BetRivers, Betway, BallyBet, BetParx, Rebet, Pinnacle

---

### 9. Find Game

**Endpoint**: `GET /api/find-game?teamA={}&teamB={}&date={}`

**Description**: Find ESPN game ID by teams and date

**Parameters**:
- `teamA`, `teamB`: Team names
- `date`: Game date (ISO format)

**Response**:
```json
{
  "success": true,
  "gameId": "18447272"
}
```

---

### 10. Game Data

**Endpoint**: `GET /api/game-data?eventId={id}`

**Description**: Basic game data from ESPN

---

### 11. Game Detail

**Endpoint**: `GET /api/game-detail?eventId={id}&teamA={}&teamB={}`

**Description**: Detailed game information including live stats

**Response Example**:
```json
{
  "gameId": "401810313",
  "status": {
    "state": "pre",
    "period": 0,
    "clock": 0,
    "displayClock": "0:00",
    "isHalftime": false,
    "isFinal": false,
    "isInProgress": false,
    "statusText": "Tue, December 30th at 8:00 PM EST"
  },
  "homeTeam": {
    "teamId": "29",
    "teamName": "Memphis Grizzlies",
    "teamAbbr": "MEM",
    "teamColor": "5d76a9",
    "score": 0,
    "players": [],
    "totals": {...},
    "leaders": {...}
  },
  "awayTeam": {...},
  "playByPlay": [],
  "periodScores": [],
  "teamComparison": [...]
}
```

---

### 12. Team Lineups

**Endpoint**: `GET /api/lineups?gameId={id}`

**Description**: Starting lineups for a game

---

### 13. Live Score

**Endpoint**: `GET /api/live-score?eventId={id}`

**Description**: Real-time score updates

---

### 14. Team Advanced Stats

**Endpoint**: `GET /api/team-advanced-stats?teamId={id}`

**Description**: Comprehensive team statistics

**Response includes**:
- Offensive stats (FG%, 3P%, FT%, PPG, APG, etc.)
- Defensive stats (DRPG, BPG, SPG, etc.)
- General stats (RPG, wins, losses, etc.)

---

### 15. Team Recent Stats

**Endpoint**: `GET /api/team-stats?team={name}&days={days}`

**Description**: Team's recent game performance

**Parameters**:
- `team`: Team name
- `days`: Number of days to look back (default: 30)

---

### 16. Play-by-Play Data

**Endpoint**: `GET /api/hupu-playbyplay?teamA={}&teamB={}`

**Description**: Play-by-play data from Hupu

---

### 17. Sina Game Data

**Endpoint**: `GET /api/sina-game?teamA={}&teamB={}`

**Description**: Game data from Sina Sports

---

### 18. Authentication

#### Get Current User
**Endpoint**: `GET /api/auth/me`

**Response**:
```json
{
  "success": true,
  "user": {
    "id": "804031822",
    "telegramId": 804031822,
    "username": null,
    "firstName": "Jonilulu",
    "lastName": null,
    "photoUrl": null,
    "role": "user",
    "status": "active",
    "createdAt": 1767083884306,
    "lastLoginAt": 1767084801433,
    "loginCount": 2
  }
}
```

#### Login Polling
**Endpoint**: `GET /api/auth/poll?token={token}`

**Description**: Poll for Telegram login completion

---

## Data Refresh Intervals

| Data Type | Refresh Interval |
|-----------|------------------|
| Smart Money Activity | 5 seconds |
| Market Prices | 30 seconds |
| Odds History | 30 seconds |
| Whale Positions | 30 seconds |
| Smart Money Positions | 30 seconds |
| Odds Comparison | 30 seconds |

---

## Authentication

The API uses cookie-based authentication with Telegram OAuth:

**Cookie Name**: `auth_session_v2`

**Cookie Value** (URL-encoded JSON):
```json
{
  "id": "804031822",
  "telegramId": 804031822,
  "username": null,
  "firstName": "Jonilulu",
  "photoUrl": null,
  "role": "user",
  "status": "active",
  "valid": true
}
```

---

## Notes for Implementation

1. **CORS**: API calls should be proxied through the frontend server to avoid CORS issues
2. **Rate Limiting**: Implement client-side rate limiting to avoid excessive API calls
3. **Caching**: Use appropriate caching strategies based on refresh intervals
4. **Error Handling**: All endpoints return standard HTTP status codes
5. **Timezone**: All timestamps are in UTC, convert to local time for display
