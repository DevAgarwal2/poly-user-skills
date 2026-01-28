# How to Determine Trader Profitability

## Quick Answer

**Yes, the AI can determine if a trader is profitable or in loss!**

Use these endpoints from the **Data API** (`https://data-api.polymarket.com`):

## Endpoints Used for Profitability

### 1. `/positions` - Active Positions (Unrealized P&L)

```bash
GET /positions?user=0x...&redeemable=false
```

**Returns:**
- `cashPnl` - Unrealized profit/loss on current positions
- `realizedPnl` - Realized P&L from partial sales (if any)

**Example Response:**
```json
[
  {
    "title": "Will Bitcoin hit $100k?",
    "cashPnl": 123.45,        // Unrealized P&L
    "realizedPnl": 50.00,     // Realized from partial sales
    "percentPnl": 15.2
  }
]
```

### 2. `/closed-positions` - Closed Positions (Realized P&L)

```bash
GET /closed-positions?user=0x...&limit=50
```

**Returns:**
- `realizedPnl` - Final profit/loss from fully closed positions

**Example Response:**
```json
[
  {
    "title": "Resolved Market",
    "realizedPnl": 200.00,    // Final realized P&L
    "avgPrice": 0.45,
    "totalBought": 100.0
  }
]
```

## Profitability Calculation

```python
# 1. Get unrealized P&L from active positions
unrealized_pnl = sum(p['cashPnl'] for p in active_positions)

# 2. Get realized P&L from partial sales (active positions)
realized_from_partials = sum(p.get('realizedPnl', 0) for p in active_positions)

# 3. Get realized P&L from fully closed positions
realized_pnl = sum(p['realizedPnl'] for p in closed_positions)

# 4. Calculate TOTAL P&L
total_realized = realized_pnl + realized_from_partials
total_pnl = unrealized_pnl + total_realized

# 5. Determine profitability
if total_pnl > 0:
    verdict = "✅ PROFITABLE"
elif total_pnl < 0:
    verdict = "❌ IN LOSS"
else:
    verdict = "⚖️  BREAK EVEN"
```

## Complete Example

### Using `trader_profitability.py`

```bash
python trader_profitability.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839
```

**Output:**
```
🚀  ✅ PROFITABLE

Total P&L: +$1,234.56 📈

────────────────────────────────────────────────────────────────────────────────
📊 P&L BREAKDOWN
────────────────────────────────────────────────────────────────────────────────
Unrealized P&L (Active Positions):  +$500.00 📈
Realized P&L (Closed Positions):    +$734.56 📈
────────────────────────────────────
TOTAL P&L:                           +$1,234.56 📈

📈 POSITION STATISTICS
────────────────────────────────────────────────────────────────────────────────
Total Positions Traded: 25
  ├─ Active: 10
  └─ Closed: 15

Winning Positions: 18 📈
  ├─ Active: 7
  └─ Closed: 11

Losing Positions: 7 📉
  ├─ Active: 3
  └─ Closed: 4

Win Rate: 72.0%
```

### Using `analyze_trader.py`

```bash
python analyze_trader.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839
```

**Output includes:**
```
📊 PORTFOLIO SUMMARY
────────────────────────────────────────────────────────────────────────────────
Status: ✅ PROFITABLE
TOTAL P&L: +$1,234.56 📈

Total Portfolio Value: $5,432.10
Active Positions: 10
Closed Positions: 15
Markets Traded: 20

💰 P&L Breakdown:
  Unrealized P&L: +$500.00 📈 (from active positions)
  Realized P&L:   +$734.56 📈 (from closed positions)

📊 Win/Loss Statistics:
  Active - Winning: 7 | Losing: 3
  Closed - Winning: 11 | Losing: 4
  Overall Win Rate: 72.0%
```

## API Calls in Code

### Python Example

```python
import requests
from utils import format_address

address = format_address("0x56687bf447db6ffa42ffe2204a05edaa20f55839")

# Get active positions
active_response = requests.get(
    "https://data-api.polymarket.com/positions",
    params={"user": address, "redeemable": "false", "limit": 500}
)
active_positions = active_response.json()

# Get closed positions
closed_response = requests.get(
    "https://data-api.polymarket.com/closed-positions",
    params={"user": address, "limit": 50}
)
closed_positions = closed_response.json()

# Calculate profitability
unrealized = sum(p.get('cashPnl', 0) for p in active_positions)
realized_partial = sum(p.get('realizedPnl', 0) for p in active_positions)
realized_closed = sum(p.get('realizedPnl', 0) for p in closed_positions)

total_pnl = unrealized + realized_partial + realized_closed

print(f"Total P&L: ${total_pnl:,.2f}")
print(f"Profitable: {total_pnl > 0}")
```

## For AI/LLM Integration

When asked "Is this trader profitable?", the AI should:

1. **Fetch active positions:**
   ```
   GET /positions?user={address}&redeemable=false&limit=500
   ```

2. **Fetch closed positions:**
   ```
   GET /closed-positions?user={address}&limit=50
   ```

3. **Calculate total P&L:**
   - Sum `cashPnl` from active positions (unrealized)
   - Sum `realizedPnl` from active positions (partial sales)
   - Sum `realizedPnl` from closed positions
   - Total = unrealized + realized

4. **Return verdict:**
   - `total_pnl > 0` → "This trader is PROFITABLE with +$X.XX total P&L"
   - `total_pnl < 0` → "This trader is IN LOSS with -$X.XX total P&L"
   - `total_pnl == 0` → "This trader is at BREAK EVEN"

## Example Prompts for AI

**User:** "Is vitalik.eth profitable on Polymarket?"

**AI Response:**
```
Let me check vitalik.eth's profitability...

[Calls /positions and /closed-positions]

✅ Yes, vitalik.eth is PROFITABLE on Polymarket.

Total P&L: +$1,234.56
- Unrealized P&L: +$500.00 (from 10 active positions)
- Realized P&L: +$734.56 (from 15 closed positions)

Win Rate: 72.0% (18 winning positions out of 25 total)
```

---

## Summary Table

| Endpoint | Purpose | Key Field | Type |
|----------|---------|-----------|------|
| `/positions?redeemable=false` | Active positions | `cashPnl` | Unrealized P&L |
| `/positions?redeemable=false` | Partial sales | `realizedPnl` | Realized P&L |
| `/closed-positions` | Fully closed | `realizedPnl` | Realized P&L |

**Formula:**
```
Total P&L = Σ(active.cashPnl) + Σ(active.realizedPnl) + Σ(closed.realizedPnl)
```

## Files to Use

1. **`trader_profitability.py`** - Dedicated profitability analysis
2. **`analyze_trader.py`** - Comprehensive profile with profitability
3. **API Reference:** `references/api.md` - Lines 43-171 (positions + closed-positions)

All examples include `import requests` and are ready to run!
