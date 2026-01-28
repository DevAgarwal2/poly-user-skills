#!/usr/bin/env python3
"""
Example: Comprehensive Trader Analysis (Workflow)

This script demonstrates a complete workflow for analyzing a trader,
combining multiple API endpoints to build a comprehensive profile.

Usage:
    python analyze_trader.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839
    python analyze_trader.py --address 0x... --top-positions 10
"""

import requests
import argparse
import sys
from datetime import datetime
from utils import format_address, format_pnl, format_percentage


def get_portfolio_value(address):
    """Get total portfolio value"""
    url = "https://data-api.polymarket.com/value"
    try:
        response = requests.get(url, params={"user": address}, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data[0].get('value', 0) if isinstance(data, list) and len(data) > 0 else 0
    except:
        return 0


def get_positions(address, limit=10):
    """Get user's current positions"""
    url = "https://data-api.polymarket.com/positions"
    try:
        response = requests.get(url, params={"user": address, "limit": limit, "sortBy": "CASHPNL", "sortDirection": "DESC"}, timeout=15)
        response.raise_for_status()
        return response.json()
    except:
        return []


def get_recent_trades(address, limit=20):
    """Get recent trading activity"""
    url = "https://data-api.polymarket.com/trades"
    try:
        response = requests.get(url, params={"user": address, "limit": limit}, timeout=15)
        response.raise_for_status()
        return response.json()
    except:
        return []


def get_markets_traded(address):
    """Get total markets traded count"""
    url = "https://data-api.polymarket.com/traded"
    try:
        response = requests.get(url, params={"user": address}, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('traded', 0)
    except:
        return 0


def get_closed_positions(address, limit=50):
    """Get closed positions with realized P&L"""
    url = "https://data-api.polymarket.com/closed-positions"
    try:
        response = requests.get(url, params={"user": address, "limit": limit}, timeout=15)
        response.raise_for_status()
        return response.json()
    except:
        return []


def analyze_trader(address, top_positions_count=5):
    """
    Perform comprehensive trader analysis.
    
    Args:
        address (str): Wallet address
        top_positions_count (int): Number of top positions to show
    
    Returns:
        dict: Comprehensive trader stats
    """
    print(f"🔍 Analyzing trader {address}...")
    print()
    
    # Fetch all data
    portfolio_value = get_portfolio_value(address)
    positions = get_positions(address, top_positions_count * 2)
    closed_positions = get_closed_positions(address, 50)
    trades = get_recent_trades(address, 100)
    markets_count = get_markets_traded(address)
    
    # Calculate statistics
    stats = {
        "address": address,
        "portfolio_value": portfolio_value,
        "active_positions": len(positions),
        "markets_traded": markets_count,
        "total_trades": len(trades),
    }
    
    # Position analysis - Calculate TOTAL P&L (unrealized + realized)
    unrealized_pnl = 0
    realized_from_partials = 0
    
    if positions:
        unrealized_pnl = sum(p.get('cashPnl', 0) for p in positions)
        realized_from_partials = sum(p.get('realizedPnl', 0) for p in positions)
        winning_positions = [p for p in positions if p.get('cashPnl', 0) > 0]
        losing_positions = [p for p in positions if p.get('cashPnl', 0) < 0]
        
        stats["total_unrealized_pnl"] = unrealized_pnl
        stats["winning_positions"] = len(winning_positions)
        stats["losing_positions"] = len(losing_positions)
    
    # Closed positions analysis
    realized_pnl = 0
    if closed_positions:
        realized_pnl = sum(p.get('realizedPnl', 0) for p in closed_positions)
        stats["closed_positions_count"] = len(closed_positions)
        stats["winning_closed"] = len([p for p in closed_positions if p.get('realizedPnl', 0) > 0])
        stats["losing_closed"] = len([p for p in closed_positions if p.get('realizedPnl', 0) < 0])
    
    # Calculate TOTAL P&L
    total_realized = realized_pnl + realized_from_partials
    total_pnl = unrealized_pnl + total_realized
    
    stats["total_realized_pnl"] = total_realized
    stats["total_pnl"] = total_pnl
    stats["is_profitable"] = total_pnl > 0
    
    # Win rate across all positions
    total_positions = len(positions) + len(closed_positions)
    if total_positions > 0:
        total_winning = stats.get("winning_positions", 0) + stats.get("winning_closed", 0)
        stats["win_rate"] = (total_winning / total_positions * 100)
    
    # Trading analysis
    if trades:
        buys = [t for t in trades if t.get('side') == 'BUY']
        sells = [t for t in trades if t.get('side') == 'SELL']
        
        total_buy_volume = sum(t.get('size', 0) * t.get('price', 0) for t in buys)
        total_sell_volume = sum(t.get('size', 0) * t.get('price', 0) for t in sells)
        
        stats["buy_trades"] = len(buys)
        stats["sell_trades"] = len(sells)
        stats["buy_volume"] = total_buy_volume
        stats["sell_volume"] = total_sell_volume
        stats["total_volume"] = total_buy_volume + total_sell_volume
    
    return stats, positions[:top_positions_count], trades[:20]


def main():
    parser = argparse.ArgumentParser(description="Comprehensive Polymarket trader analysis")
    parser.add_argument(
        "--address",
        type=str,
        required=True,
        help="Wallet address (0x...)"
    )
    parser.add_argument(
        "--top-positions",
        type=int,
        default=5,
        help="Number of top positions to display (default: 5)"
    )
    args = parser.parse_args()
    
    try:
        formatted_address = format_address(args.address)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print("=" * 100)
    print(f"COMPREHENSIVE TRADER ANALYSIS")
    print("=" * 100)
    print()
    
    # Run analysis
    stats, top_positions, recent_trades = analyze_trader(formatted_address, args.top_positions)
    
    # Display Summary
    print("📊 PORTFOLIO SUMMARY")
    print("-" * 100)
    
    # Profitability verdict
    if 'total_pnl' in stats:
        total_pnl = stats['total_pnl']
        if total_pnl > 0:
            verdict = "✅ PROFITABLE"
        elif total_pnl < 0:
            verdict = "❌ IN LOSS"
        else:
            verdict = "⚖️  BREAK EVEN"
        print(f"Status: {verdict}")
        print(f"TOTAL P&L: {format_pnl(total_pnl)}")
        print()
    
    print(f"Total Portfolio Value: ${stats['portfolio_value']:,.2f}")
    print(f"Active Positions: {stats['active_positions']}")
    print(f"Closed Positions: {stats.get('closed_positions_count', 0)}")
    print(f"Markets Traded: {stats['markets_traded']}")
    
    if 'total_unrealized_pnl' in stats:
        print(f"\n💰 P&L Breakdown:")
        print(f"  Unrealized P&L: {format_pnl(stats['total_unrealized_pnl'])} (from active positions)")
        print(f"  Realized P&L:   {format_pnl(stats.get('total_realized_pnl', 0))} (from closed positions)")
        print(f"\n📊 Win/Loss Statistics:")
        print(f"  Active - Winning: {stats['winning_positions']} | Losing: {stats['losing_positions']}")
        if 'winning_closed' in stats:
            print(f"  Closed - Winning: {stats['winning_closed']} | Losing: {stats['losing_closed']}")
        print(f"  Overall Win Rate: {stats.get('win_rate', 0):.1f}%")
    
    # Display Trading Activity
    print(f"\n\n📈 TRADING ACTIVITY")
    print("-" * 100)
    print(f"Total Trades: {stats['total_trades']}")
    
    if 'buy_trades' in stats:
        print(f"  Buy Trades: {stats['buy_trades']} (${stats['buy_volume']:,.2f})")
        print(f"  Sell Trades: {stats['sell_trades']} (${stats['sell_volume']:,.2f})")
        print(f"  Total Volume: ${stats['total_volume']:,.2f}")
    
    # Display Top Positions
    if top_positions:
        print(f"\n\n💼 TOP {len(top_positions)} POSITIONS (by P&L)")
        print("-" * 100)
        
        for i, pos in enumerate(top_positions, 1):
            print(f"\n{i}. {pos['title']}")
            print(f"   Outcome: {pos['outcome']}")
            print(f"   Size: {pos.get('size', 0):,.2f} shares @ ${pos.get('avgPrice', 0):.4f}")
            print(f"   Current: ${pos.get('currentValue', 0):,.2f}")
            
            cash_pnl = pos.get('cashPnl', 0)
            percent_pnl = pos.get('percentPnl', 0)
            print(f"   P&L: {format_pnl(cash_pnl)} ({format_percentage(percent_pnl)})")
    
    # Display Recent Trades
    if recent_trades:
        print(f"\n\n📋 RECENT TRADING ACTIVITY (Last {len(recent_trades)} trades)")
        print("-" * 100)
        
        for i, trade in enumerate(recent_trades[:10], 1):
            side = trade.get('side', 'UNKNOWN')
            side_emoji = "🟢" if side == "BUY" else "🔴"
            
            timestamp = trade.get('timestamp')
            time_str = datetime.fromtimestamp(timestamp).strftime('%m/%d %H:%M') if timestamp else 'N/A'
            
            size = trade.get('size', 0)
            price = trade.get('price', 0)
            
            print(f"{i:2d}. {time_str} | {side_emoji} {side:4s} | {size:8,.2f} @ ${price:.4f} | {trade.get('outcome', 'N/A'):3s}")
            if i == 1 or i % 5 == 0:
                print(f"     {trade.get('title', 'Unknown market')[:70]}...")
    
    print("\n" + "=" * 100)
    print("Analysis complete!")


if __name__ == "__main__":
    main()
