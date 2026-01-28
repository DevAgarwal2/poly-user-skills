# Polymarket Data API Reference

**Base URL:** `https://data-api.polymarket.com`

---

## Important: Address Format

All wallet addresses MUST be:
- **Lowercase**
- **0x-prefixed**
- **Exactly 42 characters** (0x + 40 hex)

**Example:** `0x56687bf447db6ffa42ffe2204a05edaa20f55839`

**Common Errors:**
- Using uppercase letters (e.g., `0xABC...`) → will fail
- Missing 0x prefix (e.g., `56687bf...`) → will fail
- Wrong length → will fail

**Condition IDs** must be 66 characters (0x + 64 hex).

---

## Data API Health Check

**GET** `/`

```bash
curl "https://data-api.polymarket.com/"
```

**Response:**

```json
{
  "data": "OK"
}
```

---

## User Positions

### Get Current Positions for a User

**GET** `/positions`

```bash
curl "https://data-api.polymarket.com/positions?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839&limit=20"
```

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `user` | string (required) | Wallet address (0x...) |
| `market` | string[] | Comma-separated condition IDs |
| `eventId` | int[] | Comma-separated event IDs |
| `sizeThreshold` | number | Minimum position size (default: 1) |
| `redeemable` | boolean | **IMPORTANT**: `false`=active only, `true`=claimable payouts, omitted=all positions |
| `mergeable` | boolean | Filter mergeable positions |
| `limit` | int | Results (default: 100, max: 500) |
| `offset` | int | Pagination offset (default: 0) |
| `sortBy` | string | Sort: `CURRENT`, `INITIAL`, `TOKENS`, `CASHPNL`, `PERCENTPNL`, `TITLE`, `RESOLVING`, `PRICE`, `AVGPRICE` |
| `sortDirection` | string | `ASC` or `DESC` (default: DESC) |
| `title` | string | Filter by market title (max 100 chars) |

**Response:**

```json
[
  {
    "proxyWallet": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
    "asset": "0x...",
    "conditionId": "0xdd22472e552920b8438158ea7238bfadfa4f736aa4cee91a6b86c39ead110917",
    "size": 100.5,
    "avgPrice": 0.65,
    "initialValue": 65.32,
    "currentValue": 70.25,
    "cashPnl": 4.93,
    "percentPnl": 7.55,
    "totalBought": 150.0,
    "realizedPnl": 12.50,
    "percentRealizedPnl": 19.1,
    "curPrice": 0.70,
    "redeemable": false,
    "mergeable": false,
    "title": "Will there be another US government shutdown by January 31?",
    "slug": "will-there-be-another-us-government-shutdown-by-january-31",
    "icon": "https://...",
    "eventSlug": "govt-shutdown-by",
    "outcome": "Yes",
    "outcomeIndex": 0,
    "oppositeOutcome": "No",
    "oppositeAsset": "0x...",
    "endDate": "2026-01-31T00:00:00Z",
    "negativeRisk": false
  }
]
```

**Position Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `asset` | string | Token address |
| `conditionId` | string | Market condition ID |
| `size` | number | Number of outcome tokens |
| `avgPrice` | number | Average purchase price |
| `initialValue` | number | Initial position value |
| `currentValue` | number | Current position value |
| `cashPnl` | number | Unrealized P&L |
| `percentPnl` | number | Unrealized P&L % |
| `realizedPnl` | number | Realized P&L from sales |
| `percentRealizedPnl` | number | Realized P&L % |
| `curPrice` | number | Current market price |
| `redeemable` | boolean | Can be redeemed for USDC |
| `mergeable` | boolean | Can be merged |
| `outcome` | string | "Yes" or "No" |
| `outcomeIndex` | int | 0 for Yes, 1 for No |

---

### Get Closed Positions for a User

**GET** `/closed-positions`

```bash
curl "https://data-api.polymarket.com/closed-positions?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839&limit=20"
```

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `user` | string (required) | Wallet address |
| `market` | string[] | Comma-separated condition IDs |
| `eventId` | int[] | Comma-separated event IDs |
| `title` | string | Filter by market title |
| `limit` | int | Results (default: 10, max: 50) |
| `offset` | int | Pagination offset |
| `sortBy` | string | Sort: `REALIZEDPNL`, `TITLE`, `PRICE`, `AVGPRICE`, `TIMESTAMP` |
| `sortDirection` | string | `ASC` or `DESC` |

**Response:**

```json
[
  {
    "proxyWallet": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
    "asset": "0x...",
    "conditionId": "0x...",
    "avgPrice": 0.45,
    "totalBought": 100.0,
    "realizedPnl": 55.00,
    "curPrice": 0.00,
    "timestamp": 1704067200,
    "title": "Resolved Market Question",
    "slug": "resolved-market-slug",
    "icon": "https://...",
    "eventSlug": "event-slug",
    "outcome": "Yes",
    "outcomeIndex": 0,
    "oppositeOutcome": "No",
    "oppositeAsset": "0x...",
    "endDate": "2025-01-01T00:00:00Z"
  }
]
```

**Understanding the `redeemable` Parameter:**

This is a critical parameter for position queries:

- **`redeemable=false`** → Returns ONLY current active positions (default behavior many users want)
  ```bash
  # Get only active positions
  curl "https://data-api.polymarket.com/positions?user=0x...&redeemable=false"
  ```

- **`redeemable=true`** → Returns old positions with UNCLAIMED PAYOUTS (resolved markets you haven't claimed)
  ```bash
  # Check for claimable payouts
  curl "https://data-api.polymarket.com/positions?user=0x...&redeemable=true"
  ```

- **Omit `redeemable`** → Returns ALL positions (active + redeemable)
  ```bash
  # Get everything
  curl "https://data-api.polymarket.com/positions?user=0x..."
  ```

**Use Cases:**
- Portfolio tracking → `redeemable=false`
- Find unclaimed money → `redeemable=true`
- Complete overview → omit parameter

---

## User Trades

### Get Trades for a User or Markets

**GET** `/trades`

```bash
curl "https://data-api.polymarket.com/trades?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839&limit=50"
```

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `limit` | int | Results (default: 100, max: 10000) |
| `offset` | int | Pagination offset |
| `takerOnly` | boolean | Only show taker trades (default: true) |
| `filterType` | string | `CASH` or `TOKENS` (with filterAmount) |
| `filterAmount` | number | Minimum filter value |
| `market` | string[] | Comma-separated condition IDs |
| `eventId` | int[] | Comma-separated event IDs |
| `user` | string | Wallet address |
| `side` | string | `BUY` or `SELL` |

**Response:**

```json
[
  {
    "proxyWallet": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
    "side": "BUY",
    "asset": "0x...",
    "conditionId": "0x...",
    "size": 50.0,
    "price": 0.65,
    "timestamp": 1704067200,
    "title": "Will X happen?",
    "slug": "market-slug",
    "icon": "https://...",
    "eventSlug": "event-slug",
    "outcome": "Yes",
    "outcomeIndex": 0,
    "name": "TraderName",
    "pseudonym": "trader123",
    "bio": "Full-time trader",
    "profileImage": "https://...",
    "profileImageOptimized": "https://...",
    "transactionHash": "0x..."
  }
]
```

**Trade Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `side` | string | "BUY" or "SELL" |
| `asset` | string | Token address |
| `conditionId` | string | Market condition ID |
| `size` | number | Number of tokens traded |
| `price` | number | Execution price |
| `timestamp` | int | Unix timestamp |
| `outcome` | string | "Yes" or "No" |
| `outcomeIndex` | int | 0 for Yes, 1 for No |
| `transactionHash` | string | On-chain transaction hash |

---

## User Activity

### Get User Activity

**GET** `/activity`

```bash
curl "https://data-api.polymarket.com/activity?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839&limit=50"
```

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `user` | string (required) | Wallet address |
| `limit` | int | Results (default: 100, max: 500) |
| `offset` | int | Pagination offset |
| `market` | string[] | Comma-separated condition IDs |
| `eventId` | int[] | Comma-separated event IDs |
| `type` | string[] | Filter: `TRADE`, `SPLIT`, `MERGE`, `REDEEM`, `REWARD`, `CONVERSION`, `MAKER_REBATE` |
| `start` | int | Start timestamp |
| `end` | int | End timestamp |
| `sortBy` | string | `TIMESTAMP`, `TOKENS`, or `CASH` |
| `sortDirection` | string | `ASC` or `DESC` |
| `side` | string | `BUY` or `SELL` |

**Response:**

```json
[
  {
    "proxyWallet": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
    "timestamp": 1704067200,
    "conditionId": "0x...",
    "type": "TRADE",
    "size": 25.0,
    "usdcSize": 16.25,
    "transactionHash": "0x...",
    "price": 0.65,
    "asset": "0x...",
    "side": "BUY",
    "outcomeIndex": 0,
    "title": "Will X happen?",
    "slug": "market-slug",
    "icon": "https://...",
    "eventSlug": "event-slug",
    "outcome": "Yes",
    "name": "TraderName",
    "pseudonym": "trader123",
    "bio": "Full-time trader",
    "profileImage": "https://...",
    "profileImageOptimized": "https://..."
  }
]
```

**Activity Types:**
- `TRADE` - Buy or sell order
- `SPLIT` - Split outcome tokens
- `MERGE` - Merge outcome tokens
- `REDEEM` - Redeem winning tokens
- `REWARD` - Trading rewards
- `CONVERSION` - Token conversion
- `MAKER_REBATE` - Maker rebate bonus

---

## Portfolio Value

### Get Total Value of a User's Positions

**GET** `/value`

```bash
curl "https://data-api.polymarket.com/value?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839"
```

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `user` | string (required) | Wallet address |
| `market` | string[] | Optional: filter by condition IDs |

**Response:**

```json
[
  {
    "user": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
    "value": 1523.45
  }
]
```

---

## Leaderboard

### Get Trader Leaderboard Rankings

**GET** `/v1/leaderboard`

```bash
curl "https://data-api.polymarket.com/v1/leaderboard?category=FINANCE&timePeriod=MONTH&orderBy=PNL&limit=25"
```

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `category` | string | `OVERALL`, `POLITICS`, `SPORTS`, `CRYPTO`, `CULTURE`, `MENTIONS`, `WEATHER`, `ECONOMICS`, `TECH`, `FINANCE` (default: OVERALL) |
| `timePeriod` | string | `DAY`, `WEEK`, `MONTH`, `ALL` (default: DAY) |
| `orderBy` | string | `PNL` or `VOL` (default: PNL) |
| `limit` | int | Results (default: 25, max: 50) |
| `offset` | int | Pagination offset |
| `user` | string | Filter to single user by address |
| `userName` | string | Filter to single username |

**Response:**

```json
[
  {
    "rank": "1",
    "proxyWallet": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
    "userName": "toptrader",
    "vol": 125000.50,
    "pnl": 45230.75,
    "profileImage": "https://...",
    "xUsername": "@toptrader",
    "verifiedBadge": true
  },
  {
    "rank": "2",
    "proxyWallet": "0x...",
    "userName": "profitking",
    "vol": 98500.25,
    "pnl": 32100.50,
    "profileImage": "https://...",
    "xUsername": "@profitking",
    "verifiedBadge": false
  }
]
```

**Leaderboard Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `rank` | string | Position on leaderboard |
| `proxyWallet` | string | Trader's wallet address |
| `userName` | string | Display username |
| `vol` | number | Trading volume |
| `pnl` | number | Profit and loss |
| `profileImage` | string | Profile picture URL |
| `xUsername` | string | Twitter handle |
| `verifiedBadge` | boolean | Has verified badge |

---

## User Stats

### Get Total Markets a User Has Traded

**GET** `/traded`

```bash
curl "https://data-api.polymarket.com/traded?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839"
```

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `user` | string (required) | Wallet address |

**Response:**

```json
{
  "user": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
  "traded": 42
}
```

---

## Market Holders

### Get Top Holders for Markets

**GET** `/holders`

```bash
curl "https://data-api.polymarket.com/holders?market=0xdd22472e552920b8438158ea7238bfadfa4f736aa4cee91a6b86c39ead110917&limit=10"
```

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `market` | string[] (required) | Comma-separated condition IDs |
| `limit` | int | Holders per token (default: 20, max: 20) |
| `minBalance` | int | Minimum token balance (default: 1) |

**Response:**

```json
[
  {
    "token": "0x...",
    "holders": [
      {
        "proxyWallet": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
        "asset": "0x...",
        "amount": 500.25,
        "outcomeIndex": 0,
        "name": "WhaleTrader",
        "pseudonym": "whale123",
        "bio": "Large position holder",
        "profileImage": "https://...",
        "profileImageOptimized": "https://...",
        "displayUsernamePublic": true
      }
    ]
  }
]
```

---

## Error Responses

All endpoints may return:

```json
{
  "error": "Error message"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `500` - Server Error

---

## Common Use Cases

```bash
# Get user's current portfolio
/positions?user=0x...&limit=100

# Get trading history
/trades?user=0x...&limit=100

# Get all user activity
/activity?user=0x...&limit=100

# Get portfolio value
/value?user=0x...

# Get closed positions
/closed-positions?user=0x...&limit=20

# Top finance traders this month
/v1/leaderboard?category=FINANCE&timePeriod=MONTH&orderBy=PNL&limit=25

# Top crypto traders this week
/v1/leaderboard?category=CRYPTO&timePeriod=WEEK&orderBy=VOL&limit=50

# Who holds the most of a specific market
/holders?market=0x...&limit=10

# Filter trades by market
/trades?user=0x...&market=0x...,0x...

# Filter activity by type
/activity?user=0x...&type=TRADE,REDEEM

# Get user's activity in a date range
/activity?user=0x...&start=1704067200&end=1706745600
```

---

## Notes

- All addresses must be 0x-prefixed, 40 hex characters
- Condition IDs are 0x-prefixed, 64 hex characters
- Timestamps are Unix epoch (seconds)
- Pagination uses offset/limit, not cursor-based
- No authentication required for read endpoints
- Rate limits apply - implement caching for repeated queries
