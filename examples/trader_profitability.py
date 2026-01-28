#!/usr/bin/env python3
"""
Example: Trader Profitability Analysis

This script determines if a trader is PROFITABLE or IN LOSS using:
  
  PRIMARY METHOD (Most Accurate):
    - /v1/leaderboard endpoint - Polymarket's calculated P&L
  
  SECONDARY METHOD (Manual Calculation):
    1. Unrealized P&L from active positions (/positions)
    2. Realized P&L from closed positions (/closed-positions)
    3. Total P&L = Unrealized + Realized

Usage:
    python trader_profitability.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839
    python trader_profitability.py --username noctus
    python trader_profitability.py --address 0x... --period MONTH
    python trader_profitability.py --address 0x... --detailed
"""

import requests
import argparse
import sys
from utils import format_address, format_pnl, format_percentage


def get_active_positions(address, limit=500):
    """
    Get all active positions with unrealized P&L
    
    Endpoint: /positions
    Key fields: cashPnl (unrealized), realizedPnl (if partially sold)
    """
    url = "https://data-api.polymarket.com/positions"
    try:
        response = requests.get(
            url,
            params={
                "user": address,
                "limit": limit,
                "redeemable": "false"  # Active positions only
            },
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching active positions: {e}")
        return []


def get_closed_positions(address, limit=50):
    """
    Get closed positions with realized P&L
    
    Endpoint: /closed-positions
    Key field: realizedPnl (final profit/loss from fully closed position)
    """
    url = "https://data-api.polymarket.com/closed-positions"
    try:
        response = requests.get(
            url,
            params={
                "user": address,
                "limit": limit,
                "sortBy": "REALIZEDPNL",
                "sortDirection": "DESC"
            },
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching closed positions: {e}")
        return []


def get_leaderboard_pnl(username=None, address=None, time_period="DAY"):
    """
    Get P&L from leaderboard endpoint (MOST ACCURATE)
    
    This is Polymarket's official P&L calculation.
    Use this as the primary source of truth.
    
    Args:
        username (str): Polymarket username
        address (str): Wallet address (will be formatted)
        time_period (str): DAY, WEEK, MONTH, ALL
    
    Returns:
        dict: Leaderboard data with pnl field
    """
    url = "https://data-api.polymarket.com/v1/leaderboard"
    params = {
        "category": "OVERALL",
        "timePeriod": time_period,
        "orderBy": "PNL",
        "limit": 1
    }
    
    if username:
        params["userName"] = username
    elif address:
        params["user"] = format_address(address)
    else:
        return None
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch leaderboard data: {e}")
        return None


def calculate_profitability(address, show_details=False, time_period="DAY", username=None):
    """
    Calculate total profitability (unrealized + realized P&L)
    
    Returns:
        dict: Profitability stats
    """
    print(f"🔍 Analyzing profitability for {address}...")
    print()
    
    # Fetch positions
    active_positions = get_active_positions(address)
    closed_positions = get_closed_positions(address)
    
    # Calculate unrealized P&L (from active positions)
    unrealized_pnl = 0
    unrealized_from_partials = 0  # Realized P&L from partially sold positions
    
    for pos in active_positions:
        unrealized_pnl += pos.get('cashPnl', 0)  # Current unrealized P&L
        # Some positions may have realized P&L from partial sales
        unrealized_from_partials += pos.get('realizedPnl', 0)
    
    # Calculate realized P&L (from fully closed positions)
    realized_pnl = sum(pos.get('realizedPnl', 0) for pos in closed_positions)
    
    # Total P&L = Unrealized + Realized (including partial sales)
    total_realized = realized_pnl + unrealized_from_partials
    total_pnl = unrealized_pnl + total_realized
    
    # Calculate stats
    winning_active = [p for p in active_positions if p.get('cashPnl', 0) > 0]
    losing_active = [p for p in active_positions if p.get('cashPnl', 0) < 0]
    
    winning_closed = [p for p in closed_positions if p.get('realizedPnl', 0) > 0]
    losing_closed = [p for p in closed_positions if p.get('realizedPnl', 0) < 0]
    
    total_positions = len(active_positions) + len(closed_positions)
    total_winning = len(winning_active) + len(winning_closed)
    total_losing = len(losing_active) + len(losing_closed)
    
    win_rate = (total_winning / total_positions * 100) if total_positions > 0 else 0
    
    stats = {
        "total_pnl": total_pnl,
        "unrealized_pnl": unrealized_pnl,
        "realized_pnl": total_realized,
        "active_positions": len(active_positions),
        "closed_positions": len(closed_positions),
        "total_positions": total_positions,
        "winning_active": len(winning_active),
        "losing_active": len(losing_active),
        "winning_closed": len(winning_closed),
        "losing_closed": len(losing_closed),
        "total_winning": total_winning,
        "total_losing": total_losing,
        "win_rate": win_rate,
        "is_profitable": total_pnl > 0
    }
    
    if show_details:
        stats["active_positions_data"] = active_positions
        stats["closed_positions_data"] = closed_positions
    
    return stats


def display_profitability(stats, show_details=False):
    """Display profitability analysis"""
    
    print("=" * 100)
    print("TRADER PROFITABILITY ANALYSIS")
    print("=" * 100)
    print()
    
    # Overall verdict
    total_pnl = stats["total_pnl"]
    if total_pnl > 0:
        verdict = "✅ PROFITABLE"
        emoji = "🚀"
    elif total_pnl < 0:
        verdict = "❌ IN LOSS"
        emoji = "📉"
    else:
        verdict = "⚖️  BREAK EVEN"
        emoji = "➡️"
    
    print(f"{emoji}  {verdict}")
    print(f"\nTotal P&L: {format_pnl(total_pnl)}")
    print()
    print("-" * 100)
    
    # P&L Breakdown
    print("\n📊 P&L BREAKDOWN")
    print("-" * 100)
    print(f"Unrealized P&L (Active Positions):  {format_pnl(stats['unrealized_pnl'])}")
    print(f"Realized P&L (Closed Positions):    {format_pnl(stats['realized_pnl'])}")
    print(f"{'─' * 40}")
    print(f"TOTAL P&L:                           {format_pnl(stats['total_pnl'])}")
    
    # Position Stats
    print("\n\n📈 POSITION STATISTICS")
    print("-" * 100)
    print(f"Total Positions Traded: {stats['total_positions']}")
    print(f"  ├─ Active: {stats['active_positions']}")
    print(f"  └─ Closed: {stats['closed_positions']}")
    print()
    print(f"Winning Positions: {stats['total_winning']} 📈")
    print(f"  ├─ Active: {stats['winning_active']}")
    print(f"  └─ Closed: {stats['winning_closed']}")
    print()
    print(f"Losing Positions: {stats['total_losing']} 📉")
    print(f"  ├─ Active: {stats['losing_active']}")
    print(f"  └─ Closed: {stats['losing_closed']}")
    print()
    print(f"Win Rate: {stats['win_rate']:.1f}%")
    
    # Detailed breakdown
    if show_details and "active_positions_data" in stats:
        print("\n\n💼 TOP 10 ACTIVE POSITIONS (by P&L)")
        print("-" * 100)
        
        active = sorted(
            stats["active_positions_data"],
            key=lambda x: x.get('cashPnl', 0),
            reverse=True
        )[:10]
        
        for i, pos in enumerate(active, 1):
            cash_pnl = pos.get('cashPnl', 0)
            percent_pnl = pos.get('percentPnl', 0)
            status = "📈" if cash_pnl > 0 else "📉"
            
            print(f"{i:2d}. {status} {pos.get('title', 'Unknown')[:60]}")
            print(f"     Unrealized: {format_pnl(cash_pnl)} ({format_percentage(percent_pnl)})")
            
            realized = pos.get('realizedPnl', 0)
            if realized != 0:
                print(f"     Realized (partial sales): {format_pnl(realized)}")
        
        print("\n\n💰 TOP 10 CLOSED POSITIONS (by Realized P&L)")
        print("-" * 100)
        
        closed = sorted(
            stats["closed_positions_data"],
            key=lambda x: x.get('realizedPnl', 0),
            reverse=True
        )[:10]
        
        for i, pos in enumerate(closed, 1):
            realized_pnl = pos.get('realizedPnl', 0)
            status = "📈" if realized_pnl > 0 else "📉"
            
            print(f"{i:2d}. {status} {pos.get('title', 'Unknown')[:60]}")
            print(f"     Realized P&L: {format_pnl(realized_pnl)}")
    
    print("\n" + "=" * 100)


def main():
    parser = argparse.ArgumentParser(description="Analyze trader profitability")
    parser.add_argument(
        "--address",
        type=str,
        required=True,
        help="Wallet address (0x...)"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed position breakdown"
    )
    args = parser.parse_args()
    
    try:
        formatted_address = format_address(args.address)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Calculate profitability
    stats = calculate_profitability(formatted_address, args.detailed)
    
    # Display results
    display_profitability(stats, args.detailed)
    
    # Exit code based on profitability (useful for scripting)
    sys.exit(0 if stats["is_profitable"] else 1)


if __name__ == "__main__":
    main()
