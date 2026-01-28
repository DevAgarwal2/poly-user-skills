#!/usr/bin/env python3
"""
Example: Trade Win/Loss Analysis

This script analyzes a trader's performance by checking:
  1. FAILED TRADES - Bought high, sold low (trading losses)
  2. LOST BETS - Positions that resolved against them
  3. WON BETS - Positions that resolved in their favor
  4. Win rate and profit/loss statistics

Usage:
    python trade_analysis.py --address 0xbbc022fa31796f78d91ec57d92ff29df1cf20fd0
    python trade_analysis.py --username noctus
    python trade_analysis.py --address 0x... --limit 200
"""

import requests
import argparse
import sys
from collections import defaultdict
from utils import format_address


def analyze_trades(address, limit=500):
    """
    Analyze all trades to find buy high/sell low patterns
    
    Args:
        address (str): Wallet address
        limit (int): Number of trades to analyze
    
    Returns:
        dict: Trade analysis statistics
    """
    url = "https://data-api.polymarket.com/trades"
    
    try:
        response = requests.get(
            url,
            params={
                "user": format_address(address),
                "limit": limit,
                "takerOnly": "true"
            },
            timeout=20
        )
        response.raise_for_status()
        trades = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trades: {e}")
        return None
    
    # Group trades by market
    market_trades = defaultdict(list)
    for trade in trades:
        condition_id = trade.get('conditionId')
        if condition_id:
            market_trades[condition_id].append(trade)
    
    # Analyze each market
    failed_trades = []
    
    for condition_id, trades_list in market_trades.items():
        # Sort by timestamp
        trades_list.sort(key=lambda x: x.get('timestamp', 0))
        
        buys = [t for t in trades_list if t.get('side') == 'BUY']
        sells = [t for t in trades_list if t.get('side') == 'SELL']
        
        if buys and sells:
            # Calculate average buy and sell price
            avg_buy = sum(t.get('price', 0) for t in buys) / len(buys)
            avg_sell = sum(t.get('price', 0) for t in sells) / len(sells)
            
            # Check if bought high and sold low
            if avg_sell < avg_buy:
                total_bought = sum(t.get('size', 0) for t in buys)
                total_sold = sum(t.get('size', 0) for t in sells)
                
                loss = (avg_buy - avg_sell) * min(total_bought, total_sold)
                
                failed_trades.append({
                    'title': trades_list[0].get('title', 'Unknown'),
                    'avg_buy': avg_buy,
                    'avg_sell': avg_sell,
                    'loss': loss,
                    'buy_count': len(buys),
                    'sell_count': len(sells)
                })
    
    return {
        'total_trades': len(trades),
        'failed_trades': failed_trades,
        'markets_traded': len(market_trades)
    }


def analyze_closed_positions(address, limit=50):
    """
    Analyze closed positions to find won/lost bets
    
    Args:
        address (str): Wallet address
        limit (int): Number of closed positions to check
    
    Returns:
        dict: Closed position analysis
    """
    url = "https://data-api.polymarket.com/closed-positions"
    
    try:
        response = requests.get(
            url,
            params={
                "user": format_address(address),
                "limit": limit,
                "sortBy": "TIMESTAMP",
                "sortDirection": "DESC"
            },
            timeout=15
        )
        response.raise_for_status()
        positions = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching closed positions: {e}")
        return None
    
    won_bets = []
    lost_bets = []
    
    for pos in positions:
        realized_pnl = pos.get('realizedPnl', 0)
        
        if realized_pnl > 0:
            won_bets.append(pos)
        elif realized_pnl < 0:
            lost_bets.append(pos)
    
    total_won = sum(p.get('realizedPnl', 0) for p in won_bets)
    total_lost = sum(p.get('realizedPnl', 0) for p in lost_bets)
    
    return {
        'total_closed': len(positions),
        'won_bets': won_bets,
        'lost_bets': lost_bets,
        'win_count': len(won_bets),
        'loss_count': len(lost_bets),
        'total_won': total_won,
        'total_lost': total_lost,
        'net_pnl': total_won + total_lost
    }


def analyze_open_positions(address, limit=100):
    """
    Analyze open positions to find current winners/losers
    
    Args:
        address (str): Wallet address
        limit (int): Number of positions to check
    
    Returns:
        dict: Open position analysis
    """
    url = "https://data-api.polymarket.com/positions"
    
    try:
        response = requests.get(
            url,
            params={
                "user": format_address(address),
                "limit": limit,
                "redeemable": "false"  # Active only
            },
            timeout=15
        )
        response.raise_for_status()
        positions = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching open positions: {e}")
        return None
    
    winning = [p for p in positions if p.get('cashPnl', 0) > 0]
    losing = [p for p in positions if p.get('cashPnl', 0) < 0]
    
    total_unrealized_gain = sum(p.get('cashPnl', 0) for p in winning)
    total_unrealized_loss = sum(p.get('cashPnl', 0) for p in losing)
    
    return {
        'total_open': len(positions),
        'winning_positions': winning,
        'losing_positions': losing,
        'winning_count': len(winning),
        'losing_count': len(losing),
        'unrealized_gain': total_unrealized_gain,
        'unrealized_loss': total_unrealized_loss,
        'net_unrealized': total_unrealized_gain + total_unrealized_loss
    }


def display_analysis(trade_stats, closed_stats, open_stats, address):
    """Display comprehensive trade analysis"""
    
    print("=" * 100)
    print("COMPREHENSIVE TRADE WIN/LOSS ANALYSIS")
    print("=" * 100)
    print(f"\nTrader: {address}\n")
    
    # CLOSED POSITIONS (Realized P&L)
    print("=" * 100)
    print("1. CLOSED POSITIONS (Realized P&L)")
    print("=" * 100)
    
    if closed_stats:
        print(f"\nTotal Closed Positions: {closed_stats['total_closed']}")
        print(f"  ✅ WON:  {closed_stats['win_count']} positions (+${closed_stats['total_won']:.2f})")
        print(f"  ❌ LOST: {closed_stats['loss_count']} positions (${closed_stats['total_lost']:.2f})")
        print(f"  📊 NET:  ${closed_stats['net_pnl']:+.2f}")
        
        if closed_stats['total_closed'] > 0:
            win_rate = (closed_stats['win_count'] / closed_stats['total_closed'] * 100)
            print(f"  🎯 Win Rate: {win_rate:.1f}%")
        
        # Show worst losses
        if closed_stats['lost_bets']:
            print(f"\n❌ TOP 10 LOST BETS (worst losses):")
            print("-" * 100)
            sorted_losses = sorted(closed_stats['lost_bets'], key=lambda x: x.get('realizedPnl', 0))[:10]
            for i, bet in enumerate(sorted_losses, 1):
                pnl = bet.get('realizedPnl', 0)
                title = bet.get('title', 'Unknown')[:60]
                avg_price = bet.get('avgPrice', 0)
                print(f"{i:2}. ${pnl:+7.2f} | Avg Buy: ${avg_price:.3f} | {title}")
        
        # Show best wins
        if closed_stats['won_bets']:
            print(f"\n✅ TOP 10 WON BETS (best wins):")
            print("-" * 100)
            sorted_wins = sorted(closed_stats['won_bets'], key=lambda x: x.get('realizedPnl', 0), reverse=True)[:10]
            for i, bet in enumerate(sorted_wins, 1):
                pnl = bet.get('realizedPnl', 0)
                title = bet.get('title', 'Unknown')[:60]
                avg_price = bet.get('avgPrice', 0)
                print(f"{i:2}. ${pnl:+7.2f} | Avg Buy: ${avg_price:.3f} | {title}")
    
    # OPEN POSITIONS (Unrealized P&L)
    print("\n" + "=" * 100)
    print("2. OPEN POSITIONS (Unrealized P&L)")
    print("=" * 100)
    
    if open_stats:
        print(f"\nTotal Open Positions: {open_stats['total_open']}")
        print(f"  📈 Currently Winning: {open_stats['winning_count']} (+${open_stats['unrealized_gain']:.2f})")
        print(f"  📉 Currently Losing:  {open_stats['losing_count']} (${open_stats['unrealized_loss']:.2f})")
        print(f"  📊 NET Unrealized:    ${open_stats['net_unrealized']:+.2f}")
        
        # Show biggest unrealized losses
        if open_stats['losing_positions']:
            print(f"\n📉 BIGGEST UNREALIZED LOSSES (top 10):")
            print("-" * 100)
            sorted_losing = sorted(open_stats['losing_positions'], key=lambda x: x.get('cashPnl', 0))[:10]
            for i, pos in enumerate(sorted_losing, 1):
                pnl = pos.get('cashPnl', 0)
                title = pos.get('title', 'Unknown')[:50]
                size = pos.get('size', 0)
                avg_price = pos.get('avgPrice', 0)
                cur_price = pos.get('curPrice', 0)
                print(f"{i:2}. ${pnl:+7.2f} | {size:.0f} shares | Buy ${avg_price:.3f} → Now ${cur_price:.3f} | {title}")
    
    # FAILED TRADES (Buy High, Sell Low)
    print("\n" + "=" * 100)
    print("3. FAILED TRADES (Bought High, Sold Low)")
    print("=" * 100)
    
    if trade_stats and trade_stats['failed_trades']:
        print(f"\nMarkets where trader BOUGHT HIGH and SOLD LOW: {len(trade_stats['failed_trades'])}")
        print("-" * 100)
        
        sorted_failed = sorted(trade_stats['failed_trades'], key=lambda x: x['loss'], reverse=True)[:15]
        for i, trade in enumerate(sorted_failed, 1):
            loss = trade['loss']
            avg_buy = trade['avg_buy']
            avg_sell = trade['avg_sell']
            title = trade['title'][:55]
            print(f"{i:2}. Loss: ${loss:.2f} | Buy ${avg_buy:.3f} → Sell ${avg_sell:.3f} | {title}")
    else:
        print("\nNo failed trades found (or insufficient trade data)")
    
    # OVERALL SUMMARY
    print("\n" + "=" * 100)
    print("OVERALL SUMMARY")
    print("=" * 100)
    
    total_realized = closed_stats['net_pnl'] if closed_stats else 0
    total_unrealized = open_stats['net_unrealized'] if open_stats else 0
    total_pnl = total_realized + total_unrealized
    
    print(f"\n💰 TOTAL P&L:")
    print(f"  Realized (closed):   ${total_realized:+.2f}")
    print(f"  Unrealized (open):   ${total_unrealized:+.2f}")
    print(f"  ─────────────────────────────")
    print(f"  TOTAL:               ${total_pnl:+.2f}")
    
    if total_pnl > 0:
        verdict = "✅ PROFITABLE"
    elif total_pnl < 0:
        verdict = "❌ IN LOSS"
    else:
        verdict = "⚖️  BREAK EVEN"
    
    print(f"\n🎯 VERDICT: {verdict}")
    
    # Win rate
    if closed_stats and closed_stats['total_closed'] > 0:
        total_wins = closed_stats['win_count']
        total_losses = closed_stats['loss_count']
        total_resolved = total_wins + total_losses
        
        if total_resolved > 0:
            win_rate = (total_wins / total_resolved * 100)
            print(f"📊 Win Rate (Closed): {win_rate:.1f}% ({total_wins}W / {total_losses}L)")
    
    print("\n" + "=" * 100)


def main():
    parser = argparse.ArgumentParser(description="Analyze trader win/loss performance")
    parser.add_argument(
        "--address",
        type=str,
        help="Wallet address (0x...)"
    )
    parser.add_argument(
        "--username",
        type=str,
        help="Polymarket username"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Max trades to analyze (default: 500)"
    )
    args = parser.parse_args()
    
    if not args.address and not args.username:
        print("Error: Must provide either --address or --username")
        sys.exit(1)
    
    # Get address
    if args.username:
        # For username, we'll need to use the trades endpoint directly
        address_to_use = args.username
        formatted_address = args.username
    else:
        try:
            formatted_address = format_address(args.address)
            address_to_use = args.address
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    print(f"🔍 Analyzing trader: {formatted_address}")
    print("⏳ Fetching data...\n")
    
    # Run analyses
    trade_stats = analyze_trades(address_to_use, args.limit)
    closed_stats = analyze_closed_positions(address_to_use, 50)
    open_stats = analyze_open_positions(address_to_use, 100)
    
    # Display results
    display_analysis(trade_stats, closed_stats, open_stats, formatted_address)


if __name__ == "__main__":
    main()
