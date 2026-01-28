#!/usr/bin/env python3
"""
Example: Get user's current positions

This script demonstrates how to fetch a user's current market positions
with P&L tracking, position sizes, and market details.

IMPORTANT: The 'redeemable' parameter controls which positions are returned:
  - redeemable=false (--active-only): Only CURRENT active positions
  - redeemable=true (--include-payouts): Old positions with payouts + current ones
  - redeemable not set (default): ALL positions

Usage:
    python get_user_positions.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839
    python get_user_positions.py --address 0x... --active-only   # Current positions only
    python get_user_positions.py --address 0x... --include-payouts  # Include claimable payouts
    python get_user_positions.py --address 0x... --limit 50 --sort CASHPNL
"""

import requests
import argparse
import sys
from utils import format_address, format_pnl, format_percentage


def get_user_positions(address, limit=20, sort_by="CURRENT", sort_direction="DESC", redeemable=None):
    """
    Get user's positions with P&L.
    
    Args:
        address (str): Ethereum wallet address
        limit (int): Number of positions to return (max: 500)
        sort_by (str): Sort field - CURRENT, CASHPNL, PERCENTPNL, TITLE, PRICE
        sort_direction (str): ASC or DESC
        redeemable (bool): 
            - None (default): All positions
            - False: Active positions only (no redeemable/closed)
            - True: Redeemable positions (claimable payouts)
    
    Returns:
        list: User's positions with P&L data
    """
    url = "https://data-api.polymarket.com/positions"
    params = {
        "user": format_address(address),
        "limit": limit,
        "sortBy": sort_by,
        "sortDirection": sort_direction
    }
    
    if redeemable is not None:
        params["redeemable"] = str(redeemable).lower()
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching positions: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Get Polymarket user positions")
    parser.add_argument(
        "--address",
        type=str,
        required=True,
        help="Wallet address (0x...)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max positions to fetch (default: 20, max: 500)"
    )
    parser.add_argument(
        "--sort",
        type=str,
        default="CURRENT",
        choices=["CURRENT", "CASHPNL", "PERCENTPNL", "TITLE", "PRICE"],
        help="Sort by field (default: CURRENT)"
    )
    parser.add_argument(
        "--direction",
        type=str,
        default="DESC",
        choices=["ASC", "DESC"],
        help="Sort direction (default: DESC)"
    )
    parser.add_argument(
        "--active-only",
        action="store_true",
        help="Show only ACTIVE positions (exclude redeemable/closed)"
    )
    parser.add_argument(
        "--include-payouts",
        action="store_true",
        help="Include positions with CLAIMABLE PAYOUTS (redeemable=true)"
    )
    args = parser.parse_args()
    
    # Validate mutually exclusive options
    if args.active_only and args.include_payouts:
        print("Error: Cannot use --active-only and --include-payouts together")
        sys.exit(1)
    
    try:
        formatted_address = format_address(args.address)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Determine redeemable filter
    if args.active_only:
        redeemable = False  # Only active positions
        filter_description = "ACTIVE ONLY"
    elif args.include_payouts:
        redeemable = True   # Only redeemable positions
        filter_description = "CLAIMABLE PAYOUTS ONLY"
    else:
        redeemable = None   # All positions (default)
        filter_description = "ALL POSITIONS"
    
    print(f"💼 Positions for {formatted_address} ({filter_description})")
    print("=" * 100)
    print()
    positions = get_user_positions(
        args.address,
        args.limit,
        args.sort,
        args.direction,
        redeemable
    )
    
    if not positions:
        print("No positions found or error occurred.")
        return
    
    if not isinstance(positions, list) or len(positions) == 0:
        print("No active positions.")
        return
    
    # Calculate totals
    total_value = sum(p.get('currentValue', 0) for p in positions)
    total_pnl = sum(p.get('cashPnl', 0) for p in positions)
    
    print(f"Total Positions: {len(positions)}")
    print(f"Total Value: ${total_value:,.2f}")
    print(f"Total Unrealized P&L: {format_pnl(total_pnl)}")
    print()
    print("=" * 100)
    
    for i, position in enumerate(positions, 1):
        print(f"\n{i}. {position['title']}")
        print(f"   Market: {position.get('slug', 'N/A')}")
        print(f"   Outcome: {position['outcome']} (vs {position.get('oppositeOutcome', 'N/A')})")
        
        # Position size and prices
        size = position.get('size', 0)
        avg_price = position.get('avgPrice', 0)
        cur_price = position.get('curPrice', 0)
        
        print(f"\n   Size: {size:,.2f} shares")
        print(f"   Avg Price: ${avg_price:.4f}")
        print(f"   Current Price: ${cur_price:.4f}")
        
        # P&L
        initial_value = position.get('initialValue', 0)
        current_value = position.get('currentValue', 0)
        cash_pnl = position.get('cashPnl', 0)
        percent_pnl = position.get('percentPnl', 0)
        
        print(f"\n   Initial Value: ${initial_value:,.2f}")
        print(f"   Current Value: ${current_value:,.2f}")
        print(f"   Unrealized P&L: {format_pnl(cash_pnl)} ({format_percentage(percent_pnl)})")
        
        # Realized P&L (if any)
        realized_pnl = position.get('realizedPnl')
        if realized_pnl and realized_pnl != 0:
            percent_realized = position.get('percentRealizedPnl', 0)
            print(f"   Realized P&L: {format_pnl(realized_pnl)} ({format_percentage(percent_realized)})")
        
        # Status
        if position.get('redeemable'):
            print(f"\n   Status: ✓ Redeemable")
        elif position.get('mergeable'):
            print(f"\n   Status: ⚡ Mergeable")
        
        # End date
        end_date = position.get('endDate')
        if end_date:
            print(f"   Ends: {end_date}")


if __name__ == "__main__":
    main()
