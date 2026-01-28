#!/usr/bin/env python3
"""
Example: Get Polymarket leaderboard

This script demonstrates how to fetch top traders by P&L or volume
across different categories and time periods.

Usage:
    python get_leaderboard.py
    python get_leaderboard.py --category FINANCE --period MONTH
    python get_leaderboard.py --category CRYPTO --period WEEK --order VOL
    python get_leaderboard.py --limit 50
"""

import requests
import argparse
from utils import format_pnl, format_percentage


def get_leaderboard(category="OVERALL", time_period="DAY", order_by="PNL", limit=25):
    """
    Get trader leaderboard rankings.
    
    Args:
        category (str): OVERALL, POLITICS, SPORTS, CRYPTO, CULTURE, FINANCE, TECH, ECONOMICS, WEATHER
        time_period (str): DAY, WEEK, MONTH, ALL
        order_by (str): PNL or VOL
        limit (int): Number of traders (max: 50)
    
    Returns:
        list: Leaderboard rankings
    """
    url = "https://data-api.polymarket.com/v1/leaderboard"
    params = {
        "category": category.upper(),
        "timePeriod": time_period.upper(),
        "orderBy": order_by.upper(),
        "limit": min(limit, 50)
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching leaderboard: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Get Polymarket leaderboard")
    parser.add_argument(
        "--category",
        type=str,
        default="OVERALL",
        choices=["OVERALL", "POLITICS", "SPORTS", "CRYPTO", "CULTURE", "FINANCE", "TECH", "ECONOMICS", "WEATHER", "MENTIONS"],
        help="Leaderboard category (default: OVERALL)"
    )
    parser.add_argument(
        "--period",
        type=str,
        default="DAY",
        choices=["DAY", "WEEK", "MONTH", "ALL"],
        help="Time period (default: DAY)"
    )
    parser.add_argument(
        "--order",
        type=str,
        default="PNL",
        choices=["PNL", "VOL"],
        help="Order by P&L or Volume (default: PNL)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Number of traders (default: 25, max: 50)"
    )
    args = parser.parse_args()
    
    metric = "P&L" if args.order == "PNL" else "Volume"
    
    print(f"🏆 {args.category} Leaderboard - {args.period} (Top by {metric})")
    print("=" * 100)
    print()
    
    leaderboard = get_leaderboard(args.category, args.period, args.order, args.limit)
    
    if not leaderboard:
        print("No leaderboard data found or error occurred.")
        return
    
    if not isinstance(leaderboard, list) or len(leaderboard) == 0:
        print("No traders found on leaderboard.")
        return
    
    # Display leaderboard
    for trader in leaderboard:
        rank = trader.get('rank', '?')
        username = trader.get('userName', 'Anonymous')
        pnl = trader.get('pnl', 0)
        volume = trader.get('vol', 0)
        
        # Medal for top 3
        medal = ""
        if rank == "1":
            medal = "🥇 "
        elif rank == "2":
            medal = "🥈 "
        elif rank == "3":
            medal = "🥉 "
        
        print(f"{medal}#{rank:>3}. {username}")
        print(f"       P&L: {format_pnl(pnl)}")
        print(f"       Volume: ${volume:,.2f}")
        
        # Wallet address
        wallet = trader.get('proxyWallet')
        if wallet:
            print(f"       Wallet: {wallet}")
        
        # X username
        x_username = trader.get('xUsername')
        if x_username:
            print(f"       X: {x_username}")
        
        # Verified badge
        if trader.get('verifiedBadge'):
            print(f"       ✓ Verified")
        
        print()
    
    print(f"Showing top {len(leaderboard)} traders")
    
    # Calculate totals
    total_pnl = sum(t.get('pnl', 0) for t in leaderboard)
    total_volume = sum(t.get('vol', 0) for t in leaderboard)
    
    print(f"\nCombined Stats:")
    print(f"Total P&L: {format_pnl(total_pnl)}")
    print(f"Total Volume: ${total_volume:,.2f}")


if __name__ == "__main__":
    main()
