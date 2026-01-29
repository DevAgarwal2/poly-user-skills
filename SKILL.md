---
name: polymarket-data-api
description: Access Polymarket user trading data and portfolio analytics. Get trader positions, P&L, trading history, portfolio value, leaderboards, and top holders. Use when users ask about user portfolios, trading history, P&L tracking, leaderboards, position holders, or user activity. NOT for market discovery, prices, or searching markets (use polymarket skill instead). Base URL: https://data-api.polymarket.com
---

# Polymarket Data API Quick Reference

## ⚠️ IMPORTANT: Checking Trader Profitability

When asked if a trader is profitable, **DO NOT only show winning positions**. Always check:

1. **Use leaderboard API first** (most accurate):
   ```bash
   /v1/leaderboard?userName={username}&orderBy=PNL&timePeriod=DAY
   ```
   Check `pnl` field: `> 0` = profitable, `< 0` = losing

2. **For detailed analysis**, calculate total P&L:
   - Get closed positions: `/closed-positions?user=0x...` (won/lost bets)
   - Get open positions: `/positions?user=0x...&redeemable=false` (unrealized P&L)
   - **Total P&L = Realized + Unrealized**

3. **Check BOTH wins AND losses**:
   ```python
   wins = [p for p in closed_positions if p['realizedPnl'] > 0]
   losses = [p for p in closed_positions if p['realizedPnl'] < 0]
   net_pnl = sum(p['realizedPnl'] for p in closed_positions)
   ```

**❌ WRONG:** Only showing top 10 wins (cherry-picking data)  
**✅ CORRECT:** Show wins, losses, and net P&L

## Base URL

```
https://data-api.polymarket.com
```

## Quick Start

```bash
# User's current positions (with P&L)
/positions?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839&limit=20

# User's current positions only (exclude closed/redeemable markets)
/positions?user=0x56687bf447db6ffa42ffe2204a05edaa20f55839&limit=100&redeemable=false

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

## Address Format (CRITICAL)

Wallet addresses MUST be lowercase, 0x-prefixed, exactly 42 characters:

```python
# Format address correctly
def format_address(address):
    """Ensure address is lowercase, 0x-prefixed, 42 chars"""
    clean = address.lower().replace('0x', '')
    if len(clean) != 40:
        raise ValueError(f"Invalid address length: {len(clean)} (expected 40)")
    if not all(c in '0123456789abcdef' for c in clean):
        raise ValueError("Invalid hex characters in address")
    return f"0x{clean}"

# Example usage
address = "0xABC123..."  # ❌ Wrong (uppercase)
address = format_address(address)  # ✓ Correct: "0xabc123..."
```

**Condition IDs** must be 66 characters (0x + 64 hex). Same formatting rules apply.

## Making API Calls

Use the `requests` library with properly formatted addresses:

```python
import requests

# Format the address first
user_address = format_address("0x56687BF447Db6fFa42fFe2204a05EdAA20f55839")

# Get user's current positions
response = requests.get(
    "https://data-api.polymarket.com/positions",
    params={"user": user_address, "limit": 20}
)
positions = response.json()

# Get portfolio value
value_response = requests.get(
    "https://data-api.polymarket.com/value",
    params={"user": user_address}
)
portfolio_value = value_response.json()[0]["value"]

# Get top finance traders this month
leaderboard = requests.get(
    "https://data-api.polymarket.com/v1/leaderboard",
    params={
        "category": "FINANCE",
        "timePeriod": "MONTH",
        "orderBy": "PNL",
        "limit": 25
    }
).json()
```

## Common Tasks

| Task | Endpoint |
|------|----------|
| **Check profitability** | `/v1/leaderboard?userName={username}\u0026orderBy=PNL` |
| Current positions | `/positions?user={address}` |
| Won/lost bets | `/closed-positions?user={address}` |
| Trade history | `/trades?user={address}` |
| User activity | `/activity?user={address}` |
| Portfolio value | `/value?user={address}` |
| Markets traded | `/traded?user={address}` |
| Leaderboard rankings | `/v1/leaderboard?category={category}\u0026timePeriod={period}` |
| Market holders | `/holders?market={condition_id}` |
| API health | `/` |

## Key Parameters

**User Endpoints:** `user` (required, 42-char address), `limit`, `offset`, `sortBy` (CURRENT, CASHPNL, PERCENTPNL, TITLE), `sortDirection` (ASC/DESC), `redeemable` (false to exclude finished markets)

**Leaderboard:** `category` (OVERALL, POLITICS, SPORTS, CRYPTO, CULTURE, FINANCE, TECH, ECONOMICS, WEATHER), `timePeriod` (DAY, WEEK, MONTH, ALL), `orderBy` (PNL, VOL), `limit` (max 50)

**Activity:** `type` (TRADE, SPLIT, MERGE, REDEEM, REWARD, CONVERSION, MAKER_REBATE), `side` (BUY, SELL), `start`/`end` (Unix timestamps)

See [api.md](references/api.md) for complete parameter documentation.

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

**Check if a trader is profitable (RECOMMENDED):**
1. Use leaderboard API: `/v1/leaderboard?userName={username}\u0026orderBy=PNL`
2. Check `pnl` field: positive = profitable, negative = losing
3. For details: get closed positions `/closed-positions?user=0x...` and open positions `/positions?user=0x...\u0026redeemable=false`

**Analyze a trader's complete performance:**
1. Get leaderboard P\u0026L: `/v1/leaderboard?userName={username}`
2. Get closed positions (won/lost bets): `/closed-positions?user=0x...\u0026limit=50`
3. Get open positions (unrealized P\u0026L): `/positions?user=0x...\u0026redeemable=false`
4. Get trade history: `/trades?user=0x...\u0026limit=100`
5. Calculate: Total P\u0026L = Realized + Unrealized

**Find top traders:**
1. Get leaderboard: `/v1/leaderboard?category=FINANCE\u0026timePeriod=MONTH\u0026orderBy=PNL\u0026limit=25`
2. Check specific trader: `/positions?user={trader_address}`

**Analyze a market's holders:**
1. Get top holders: `/holders?market={condition_id}\u0026limit=10`
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

## Python Examples

The `examples/` directory contains complete, runnable scripts with proper address formatting:

### User Analysis
- **`get_user_positions.py`** - Current positions with P\u0026L (supports --active-only, --include-payouts)
- **`get_user_trades.py`** - Trading history
- **`get_user_activity.py`** - Complete activity (trades, splits, merges, redeems, rewards)
- **`get_portfolio_value.py`** - Total portfolio value

### Profitability Analysis
- **`trader_profitability.py`** - Check if trader is profitable (uses leaderboard API)
- **`trade_analysis.py`** - Complete win/loss analysis (shows won bets, lost bets, failed trades)
- **`analyze_trader.py`** - Complete trader profile with P\u0026L breakdown

### Leaderboards & Markets
- **`get_leaderboard.py`** - Top traders by category/period
- **`get_market_holders.py`** - Top holders for a market

### Utilities
- **`utils.py`** - Address formatting, P\u0026L formatting, validation
- **`redeemable_parameter_demo.py`** - Demo of redeemable parameter behavior

Each script includes address validation and formatted output. Run with `--help` for usage:

```bash
# Check profitability
python examples/trader_profitability.py --username noctus
python examples/trade_analysis.py --address 0x...

# Get positions
python examples/get_user_positions.py --address 0x... --active-only

# Complete analysis
python examples/analyze_trader.py --address 0x...
```

**Important:** All scripts use `utils.format_address()` to ensure addresses are properly formatted (lowercase, 0x-prefixed, 42 chars).

See `examples/README.md` for complete documentation and workflows.

## References

- **Full API Docs**: See [references/api.md](references/api.md)
- **Profitability Guide**: See [references/PROFITABILITY_GUIDE.md](references/PROFITABILITY_GUIDE.md) - How to check if traders are profitable
- **Trade Analysis Guide**: See [references/TRADE_ANALYSIS_GUIDE.md](references/TRADE_ANALYSIS_GUIDE.md) - Finding won/lost bets and failed trades
- **Endpoint Coverage**: See [references/ENDPOINT_COVERAGE.md](references/ENDPOINT_COVERAGE.md) - All 8 endpoints covered
- **Examples**: See [examples/README.md](examples/README.md) - Python usage examples

## File Structure

```
polymarket-data-api/
├── SKILL.md                          # Main skill definition
├── references/                       # 📚 Reference documentation
│   ├── api.md                       # Complete API documentation
│   ├── PROFITABILITY_GUIDE.md       # How to check profitability
│   ├── TRADE_ANALYSIS_GUIDE.md      # Win/loss analysis guide
│   └── ENDPOINT_COVERAGE.md         # Endpoint coverage checklist
└── examples/                         # 🐍 Python examples
    ├── README.md                    # Examples documentation
    ├── utils.py                     # Shared utilities
    ├── get_user_positions.py        # User positions with P&L
    ├── get_user_trades.py           # Trading history
    ├── get_user_activity.py         # Complete activity log
    ├── get_portfolio_value.py       # Portfolio value
    ├── get_leaderboard.py           # Trader rankings
    ├── get_market_holders.py        # Market top holders
    ├── trader_profitability.py      # Check if profitable
    ├── trade_analysis.py            # Complete win/loss analysis
    ├── analyze_trader.py            # Full trader profile
    └── redeemable_parameter_demo.py # Demo: redeemable parameter
```
