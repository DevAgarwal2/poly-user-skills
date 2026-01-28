# Trade Win/Loss Analysis Guide

## How to Check If a Trader is Really Profitable

### ⚠️ Important: Don't Trust Incomplete Data!

The previous analysis was **WRONG** because it only showed winning trades. Always check:

1. ✅ **LOST BETS** - Markets that resolved against the trader
2. ✅ **FAILED TRADES** - Bought high, sold low
3. ✅ **UNREALIZED LOSSES** - Open positions currently losing
4. ✅ **TOTAL P&L** - Realized + Unrealized

---

## Quick Check: Use the Leaderboard API

**This is the EASIEST and MOST ACCURATE method:**

```python
import requests

url = "https://data-api.polymarket.com/v1/leaderboard?category=OVERALL&timePeriod=DAY&orderBy=PNL&limit=1&userName=noctus"
response = requests.get(url)
data = response.json()

pnl = data[0]['pnl']
print(f"P&L: ${pnl:+.2f}")

if pnl > 0:
    print("✅ PROFITABLE")
elif pnl < 0:
    print("❌ IN LOSS")
```

**Example Result for Noctus:**
```json
{
  "rank": "275303",
  "userName": "Noctus",
  "pnl": -0.51,  // ❌ LOSING $0.51 today
  "vol": 0
}
```

---

## Comprehensive Analysis

For detailed win/loss breakdown, use the new `trade_analysis.py`:

```bash
cd /Users/devagarwal/Documents/polymarket-proj/polymarket-data-api/examples

# Analyze by address
python3 trade_analysis.py --address 0xbbc022fa31796f78d91ec57d92ff29df1cf20fd0

# Analyze by username
python3 trade_analysis.py --username noctus

# Analyze more trades
python3 trade_analysis.py --address 0x... --limit 1000
```

### What It Checks:

#### 1. **Closed Positions (Realized P&L)**
- ✅ Won bets (markets resolved in their favor)
- ❌ Lost bets (markets resolved against them)
- Net realized profit/loss

#### 2. **Open Positions (Unrealized P&L)**
- 📈 Currently winning positions
- 📉 Currently losing positions  
- Net unrealized profit/loss

#### 3. **Failed Trades (Buy High, Sell Low)**
- Markets where they bought at higher price
- Then sold at lower price
- = Trading loss (not bet loss)

#### 4. **Overall Summary**
```
TOTAL P&L = Realized + Unrealized
```

---

## Example Output:

```
============================================================
COMPREHENSIVE TRADE WIN/LOSS ANALYSIS
============================================================

Trader: 0xbbc022fa31796f78d91ec57d92ff29df1cf20fd0

============================================================
1. CLOSED POSITIONS (Realized P&L)
============================================================

Total Closed Positions: 150
  ✅ WON:  90 positions (+$500.00)
  ❌ LOST: 60 positions ($-450.00)
  📊 NET:  $+50.00
  🎯 Win Rate: 60.0%

❌ TOP 10 LOST BETS (worst losses):
────────────────────────────────────────────────────────────
 1. $-25.00 | Avg Buy: $0.750 | Trump wins popular vote
 2. $-20.00 | Avg Buy: $0.650 | Bitcoin hits $100k
 3. $-15.00 | Avg Buy: $0.500 | AI regulation by Q1

✅ TOP 10 WON BETS (best wins):
────────────────────────────────────────────────────────────
 1. $+50.00 | Avg Buy: $0.100 | Anthropic top model
 2. $+45.00 | Avg Buy: $0.150 | Google top model
 3. $+40.00 | Avg Buy: $0.200 | IPL match winner

============================================================
2. OPEN POSITIONS (Unrealized P&L)
============================================================

Total Open Positions: 25
  📈 Currently Winning: 10 (+$75.00)
  📉 Currently Losing:  15 ($-100.00)
  📊 NET Unrealized:    $-25.00

📉 BIGGEST UNREALIZED LOSSES (top 10):
────────────────────────────────────────────────────────────
 1. $-15.00 | 300 shares | Buy $0.100 → Now $0.050 | Market XYZ
 2. $-10.00 | 200 shares | Buy $0.200 → Now $0.150 | Market ABC

============================================================
3. FAILED TRADES (Bought High, Sold Low)
============================================================

Markets where trader BOUGHT HIGH and SOLD LOW: 8
────────────────────────────────────────────────────────────
 1. Loss: $12.00 | Buy $0.750 → Sell $0.700 | Trump election
 2. Loss: $8.00  | Buy $0.500 → Sell $0.450 | Bitcoin price

============================================================
OVERALL SUMMARY
============================================================

💰 TOTAL P&L:
  Realized (closed):   $+50.00
  Unrealized (open):   $-25.00
  ─────────────────────────────────
  TOTAL:               $+25.00

🎯 VERDICT: ✅ PROFITABLE
📊 Win Rate (Closed): 60.0% (90W / 60L)

============================================================
```

---

## Common Mistakes When Analyzing Traders:

### ❌ WRONG: Only Looking at Winners
```python
# This only shows TOP 10 WINS - misleading!
sorted_wins = sorted(positions, key=lambda x: x['realizedPnl'], reverse=True)[:10]
```

### ✅ CORRECT: Check Both Wins AND Losses
```python
# Separate wins and losses
wins = [p for p in positions if p['realizedPnl'] > 0]
losses = [p for p in positions if p['realizedPnl'] < 0]

total_won = sum(p['realizedPnl'] for p in wins)
total_lost = sum(p['realizedPnl'] for p in losses)

net_pnl = total_won + total_lost  # This is the REAL P&L
```

---

## API Endpoints Used:

| Endpoint | What It Returns |
|----------|-----------------|
| `/v1/leaderboard?userName=X` | **Official P&L** (use this!) |
| `/closed-positions?user=0x...` | Realized P&L (won/lost bets) |
| `/positions?user=0x...&redeemable=false` | Unrealized P&L (open positions) |
| `/trades?user=0x...` | Trade history (for buy high/sell low analysis) |

---

## For AI/LLM Integration:

When asked "Is this trader profitable?", the AI should:

1. **FIRST**: Check `/v1/leaderboard` for official P&L
2. **THEN**: Get detailed breakdown:
   - Fetch `/closed-positions` → separate wins/losses
   - Fetch `/positions` → check unrealized losses
   - Fetch `/trades` → find failed trades (buy high/sell low)
3. **CALCULATE**: Total P&L = Realized + Unrealized
4. **REPORT**: Both wins AND losses, not just wins!

### Example AI Response:

**User:** "Is Noctus profitable?"

**AI:** 
```
Let me check Noctus's trading performance...

[Calls /v1/leaderboard API]

❌ Noctus is currently IN LOSS

Performance Summary:
- Today's P&L: -$0.51
- Leaderboard Rank: #275,303

Detailed Breakdown:
- Closed Positions: 150 total
  ✅ Won: 90 bets (+$500)
  ❌ Lost: 60 bets (-$450)
  Net Realized: +$50

- Open Positions: 25 total
  📈 Winning: 10 positions (+$75)
  📉 Losing: 15 positions (-$100)
  Net Unrealized: -$25

- Failed Trades: 8 markets where bought high, sold low

TOTAL P&L: +$25.00 (all-time)
TODAY: -$0.51 (losing)

Verdict: Slightly profitable overall, but losing today.
```

---

## Files to Use:

1. **`trade_analysis.py`** - Complete win/loss breakdown
2. **`trader_profitability.py`** - Uses leaderboard API (most accurate)
3. **`analyze_trader.py`** - General trader profile
