---
name: polymarket-data-api
description: Access Polymarket user trading data and portfolio analytics. Get trader positions, P&L, trading history, portfolio value, leaderboards, and top holders. Use for user analytics, NOT market discovery. Base URL: https://data-api.polymarket.com
---

# Polymarket Data API Quick Reference

## When to Use This Skill

Use this skill when users ask about:
- **User portfolios**: "Show me this trader's positions", "What's their portfolio worth?"
- **Trading history**: "What did this wallet trade?", "Show their recent trades"
- **P&L tracking**: "How much has this trader made?", "Show profit/loss"
- **Leaderboards**: "Who are the top traders?", "Show the finance leaderboard"
- **Position holders**: "Who owns the most of this market?"
- **User activity**: "What has this address been doing?"

**Don't use for:** Market discovery, prices, or searching markets (use polymarket skill instead)

## Base URL

```
https://data-api.polymarket.com
```

## Quick Start

```bash
# User's current positions (with P&L)
/positions?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839&limit=20

# User's trading history
/trades?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839&limit=50

# User's all activity
/activity?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839&limit=50

# Portfolio total value
/value?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839

# Closed/settled positions
/closed-positions?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839&limit=20

# Trader leaderboard (FINANCE category, MONTH period)
/v1/leaderboard?category=FINANCE&timePeriod=MONTH&orderBy=PNL&limit=25

# Top holders for a market
/holders?market=0xdd22472e552920b8438158ea7238bfadfa4f736aa4cee91a6b86c39ead110917&limit=10
```

## Common Tasks

| Task | Endpoint |
|------|----------|
| Current positions | `/positions?user={address}` |
| Trade history | `/trades?user={address}` |
| User activity | `/activity?user={address}` |
| Portfolio value | `/value?user={address}` |
| Closed positions | `/closed-positions?user={address}` |
| Markets traded | `/traded?user={address}` |
| Leaderboard | `/v1/leaderboard?category={category}&timePeriod={period}` |
| Market holders | `/holders?market={condition_id}` |
| API health | `/` |

## Key Parameters

### User Endpoints
- `user` (required) - Ethereum wallet address (format: 0x... 42 chars)
- `limit` - Results per page (max varies by endpoint)
- `offset` - Pagination offset (default: 0)
- `sortBy` - Position sorting: `CURRENT`, `CASHPNL`, `PERCENTPNL`, `TITLE`, etc.
- `sortDirection` - `ASC` or `DESC`

### Leaderboard
- `category` - `OVERALL`, `POLITICS`, `SPORTS`, `CRYPTO`, `CULTURE`, `FINANCE`, `TECH`, `ECONOMICS`, `WEATHER`, `MENTIONS`
- `timePeriod` - `DAY`, `WEEK`, `MONTH`, `ALL` (default: DAY)
- `orderBy` - `PNL` or `VOL` (default: PNL)
- `limit` - Max 50 (default: 25)

### Activity Filtering
- `type` - `TRADE`, `SPLIT`, `MERGE`, `REDEEM`, `REWARD`, `CONVERSION`, `MAKER_REBATE`
- `side` - `BUY` or `SELL`
- `start` / `end` - Unix timestamps

## Error Handling

- **400 Bad Request**: Invalid parameters (check address format: 0x + 40 hex chars)
- **404 Not Found**: User has no data or invalid endpoint
- **500 Server Error**: Retry with backoff

**Common Issues:**
- Addresses must be 42 chars lowercase (0x + 40 hex)
- Condition IDs must be 66 chars (0x + 64 hex)
- Empty results = empty array, not error
- Category and timePeriod values are UPPERCASE
- No auth required for all endpoints

## Example Workflows

**Analyze a trader:**
1. Get positions: `/positions?user=0x...`
2. Get recent trades: `/trades?user=0x...&limit=20`
3. Get portfolio value: `/value?user=0x...`

**Find top traders:**
1. Get leaderboard: `/v1/leaderboard?category=FINANCE&timePeriod=MONTH&orderBy=PNL&limit=25`
2. Check specific trader: `/positions?user={trader_address}`

**Analyze a market's holders:**
1. Get top holders: `/holders?market={condition_id}&limit=10`
2. Check their positions: `/positions?user={holder_address}`

## Quick Reference: Which Skill to Use?

| User asks about... | Use this skill |
|-------------------|----------------|
| "Find markets about X" | polymarket ✗ |
| "What are the odds for X?" | polymarket ✗ |
| "Show me crypto markets" | polymarket ✗ |
| "What's this trader's portfolio?" | polymarket-data-api ✓ |
| "Show me their trades" | polymarket-data-api ✓ |
| "Who are the top traders?" | polymarket-data-api ✓ |
| "What's their P&L?" | polymarket-data-api ✓ |

## Related Skills

- Use **polymarket** (Gamma API) for market discovery and prices
- Use **polymarket-data-api** (Data API) for user trading data and portfolios
- Often you'll need BOTH: Search for markets with Gamma API, then get user positions with Data API

## References

- **Full API Docs**: See [API.md](references/api.md)
