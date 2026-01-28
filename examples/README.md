# Polymarket Data API - Python Examples

This directory contains complete, runnable Python scripts demonstrating how to use the Polymarket Data API for user trading analytics and portfolio tracking.

## Available Examples

### User Analytics

#### `get_user_positions.py`
Get a user's current market positions with P&L tracking.

```bash
# Get all positions (active + redeemable)
python get_user_positions.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839

# Get only ACTIVE positions (exclude claimable payouts)
python get_user_positions.py --address 0x... --active-only

# Get only positions with CLAIMABLE PAYOUTS
python get_user_positions.py --address 0x... --include-payouts

# Get top 50 active positions sorted by P&L
python get_user_positions.py --address 0x... --limit 50 --active-only --sort CASHPNL
```

**Understanding the `redeemable` parameter:**
- `--active-only` (redeemable=false) → Only current active positions
- `--include-payouts` (redeemable=true) → Old positions with unclaimed payouts
- No flag (default) → All positions (active + redeemable)

**Use cases:**
- Track position performance
- Calculate unrealized P&L
- Monitor portfolio composition
- Find unclaimed payouts from resolved markets

---

#### `redeemable_parameter_demo.py`
Interactive demonstration of the `redeemable` parameter behavior.

```bash
# Compare all three query types
python redeemable_parameter_demo.py 0x56687bf447db6ffa42ffe2204a05edaa20f55839
```

**Shows:**
- Active positions only (redeemable=false)
- Claimable payouts only (redeemable=true)
- All positions (no parameter)
- Side-by-side comparison with explanations

---

#### `get_user_trades.py`
Get a user's complete trading history.

```bash
# Get last 50 trades
python get_user_trades.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839

# Get last 100 BUY trades only
python get_user_trades.py --address 0x... --limit 100 --side BUY

# Get all SELL trades
python get_user_trades.py --address 0x... --limit 1000 --side SELL
```

**Use cases:**
- Analyze trading patterns
- Calculate buy/sell ratios
- Track trade timing

---

#### `get_user_activity.py`
Get user's complete activity history including trades, splits, merges, redeems, and rewards.

```bash
# Get all recent activity
python get_user_activity.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839

# Get only trades and redemptions
python get_user_activity.py --address 0x... --type TRADE,REDEEM --limit 100

# Get only buy trades
python get_user_activity.py --address 0x... --type TRADE --side BUY

# Get rewards and rebates
python get_user_activity.py --address 0x... --type REWARD,MAKER_REBATE
```

**Activity types:**
- `TRADE` - Buy/sell orders
- `SPLIT` - Split outcome tokens
- `MERGE` - Merge outcome tokens
- `REDEEM` - Redeem winning tokens
- `REWARD` - Trading rewards
- `CONVERSION` - Token conversions
- `MAKER_REBATE` - Maker rebate bonuses

**Use cases:**
- Complete transaction history
- Track reward earnings
- Monitor token operations (splits/merges)
- Calculate total fees paid
- Build activity timeline

**Difference from `/trades`:**
- `/trades` → Only BUY/SELL trades
- `/activity` → All transaction types (more comprehensive)

---

#### `get_portfolio_value.py`
Get total value of a user's positions.

```bash
# Get portfolio value
python get_portfolio_value.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839

# Get detailed stats (positions count, markets traded)
python get_portfolio_value.py --address 0x... --detailed
```

**Use cases:**
- Track portfolio value over time
- Calculate position concentration
- Monitor account balance

---

### Leaderboards

#### `get_leaderboard.py`
Get top traders by P&L or volume across categories.

```bash
# Overall leaderboard (daily P&L)
python get_leaderboard.py

# Finance traders this month
python get_leaderboard.py --category FINANCE --period MONTH

# Top crypto traders by volume this week
python get_leaderboard.py --category CRYPTO --period WEEK --order VOL

# Top 50 all-time traders
python get_leaderboard.py --period ALL --limit 50
```

**Categories:** OVERALL, POLITICS, SPORTS, CRYPTO, CULTURE, FINANCE, TECH, ECONOMICS, WEATHER, MENTIONS

**Use cases:**
- Find top performers
- Track competitive rankings
- Discover successful traders

---

### Market Analytics

#### `get_market_holders.py`
Get top position holders for a specific market.

```bash
# Get top 10 holders
python get_market_holders.py --market 0xdd22472e552920b8438158ea7238bfadfa4f736aa4cee91a6b86c39ead110917

# Get top 20 holders
python get_market_holders.py --market 0x... --limit 20
```

**Use cases:**
- Analyze market concentration
- Identify whale positions
- Track smart money

---

### Workflows

#### `analyze_trader.py`
Comprehensive trader analysis combining multiple endpoints.

```bash
# Full trader analysis with PROFITABILITY VERDICT
python analyze_trader.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839

# Show top 10 positions
python analyze_trader.py --address 0x... --top-positions 10
```

**Provides:**
- **✅ PROFITABILITY VERDICT** (Profitable / In Loss / Break Even)
- **Total P&L** (Unrealized + Realized)
- Portfolio summary
- Win/loss statistics across active and closed positions
- Trading activity stats
- Top positions by P&L
- Recent trading history

**Endpoints used:**
- `/value` - Portfolio value
- `/positions` - Active positions with unrealized P&L
- `/closed-positions` - Closed positions with realized P&L
- `/trades` - Trading history
- `/traded` - Markets traded count

---

#### `trader_profitability.py`
Dedicated profitability analysis showing if a trader is profitable or in loss.

```bash
# Quick profitability check (uses leaderboard API - most accurate)
python trader_profitability.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839
python trader_profitability.py --username noctus

# Check different time periods
python trader_profitability.py --username noctus --period DAY
python trader_profitability.py --username noctus --period MONTH
python trader_profitability.py --username noctus --period ALL

# Detailed breakdown with top positions
python trader_profitability.py --address 0x... --detailed
```

**Shows:**
- Overall verdict: PROFITABLE / IN LOSS / BREAK EVEN
- Total P&L breakdown (unrealized + realized)
- Position statistics (winning vs losing)
- Win rate percentage
- Top 10 best/worst positions (with --detailed flag)

**Calculation:**
```
Total P&L = Unrealized P&L (active) + Realized P&L (closed + partial sales)
```

**Endpoints used:**
- `/v1/leaderboard` - Official Polymarket P&L (primary source)
- `/positions?redeemable=false` - Active positions
- `/closed-positions` - Fully closed positions

---

#### `trade_analysis.py` ⭐ NEW
**Complete win/loss analysis** - Checks failed trades, lost bets, and unrealized losses.

```bash
# Comprehensive analysis
python trade_analysis.py --address 0xbbc022fa31796f78d91ec57d92ff29df1cf20fd0
python trade_analysis.py --username noctus

# Analyze more trades
python trade_analysis.py --address 0x... --limit 1000
```

**Shows:**
1. **Closed Positions** - Won bets vs Lost bets (realized P&L)
2. **Open Positions** - Currently winning vs losing (unrealized P&L)
3. **Failed Trades** - Markets where bought high, sold low
4. **Overall Summary** - Total P&L, win rate, verdict

**Use this to:**
- ❌ Find LOST BETS (markets resolved against trader)
- 📉 Find UNREALIZED LOSSES (open positions losing money)
- 💸 Find FAILED TRADES (bought high, sold low)
- ✅ Get TRUE profitability (not just winners!)

**Endpoints used:**
- `/trades` - Trade history
- `/closed-positions` - Realized P&L with wins/losses
- `/positions` - Unrealized P&L

---

## Utility Module

### `utils.py`
Shared helper functions for address formatting and validation.

```python
from utils import format_address, format_condition_id

# Format wallet address (CRITICAL - addresses must be lowercase!)
address = format_address("0xABC123...")  # Returns: "0xabc123..."

# Format condition ID
condition_id = format_condition_id("0xDD22...")  # Returns: "0xdd22..."

# Format P&L with indicators
from utils import format_pnl, format_percentage
pnl_str = format_pnl(1234.56)  # Returns: "+$1,234.56 📈"
pct_str = format_percentage(-5.2)  # Returns: "-5.20% 📉"
```

---

## Address Format (CRITICAL!)

**All wallet addresses MUST be:**
- Lowercase
- 0x-prefixed
- Exactly 42 characters (0x + 40 hex)

**All condition IDs MUST be:**
- Lowercase
- 0x-prefixed
- Exactly 66 characters (0x + 64 hex)

The `utils.py` module handles this automatically. Always use `format_address()` and `format_condition_id()` before making API calls!

```python
# ❌ WRONG - Will fail!
requests.get(url, params={"user": "0xABC123..."})

# ✓ CORRECT
from utils import format_address
requests.get(url, params={"user": format_address("0xABC123...")})
```

---

## Common Patterns

### Basic API Call with Address Formatting
```python
import requests
from utils import format_address

address = format_address("0xABC...")

response = requests.get(
    "https://data-api.polymarket.com/positions",
    params={"user": address, "limit": 20}
)
positions = response.json()
```

### Error Handling
```python
try:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    return None
```

### Pagination
```python
# First page
params = {"user": address, "limit": 100, "offset": 0}

# Second page
params = {"user": address, "limit": 100, "offset": 100}
```

---

## API Response Formats

### Positions
```python
[
    {
        "proxyWallet": "0x...",
        "asset": "0x...",
        "conditionId": "0x...",
        "size": 100.5,
        "avgPrice": 0.65,
        "initialValue": 65.32,
        "currentValue": 70.25,
        "cashPnl": 4.93,
        "percentPnl": 7.55,
        "title": "Market question?",
        "slug": "market-slug",
        "outcome": "Yes"
    }
]
```

### Trades
```python
[
    {
        "proxyWallet": "0x...",
        "side": "BUY",
        "size": 50.0,
        "price": 0.65,
        "timestamp": 1704067200,
        "title": "Market question?",
        "outcome": "Yes",
        "transactionHash": "0x..."
    }
]
```

### Leaderboard
```python
[
    {
        "rank": "1",
        "proxyWallet": "0x...",
        "userName": "toptrader",
        "pnl": 45230.75,
        "vol": 125000.50,
        "verifiedBadge": true
    }
]
```

---

## Tips

1. **Always format addresses**: Use `format_address()` from `utils.py` - this is critical!
2. **Check for empty results**: API returns `[]` or `{}`, not errors, for no data
3. **No authentication required**: All endpoints are public
4. **Rate limiting**: Be respectful with requests
5. **Category values are UPPERCASE**: FINANCE, CRYPTO, etc.
6. **Time period values are UPPERCASE**: DAY, WEEK, MONTH, ALL
7. **Combine with Gamma API**: Use Data API for user data, Gamma API for market discovery

---

## Example Workflow

```bash
# 1. Find a trader on the leaderboard
python get_leaderboard.py --category FINANCE --period MONTH

# 2. Get their wallet address, then analyze them
python analyze_trader.py --address 0x...

# 3. Check their current positions
python get_user_positions.py --address 0x... --limit 50

# 4. Review their trading history
python get_user_trades.py --address 0x... --limit 100

# 5. Check which markets they're in
python get_market_holders.py --market 0x...
```

---

## Related Resources

- **SKILL.md**: Quick reference guide
- **references/api.md**: Complete API documentation
- **utils.py**: Shared utility functions

## Support

For issues or questions about the Polymarket Data API, refer to:
- Polymarket official documentation
- API reference in `references/api.md`
