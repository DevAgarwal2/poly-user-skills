#!/usr/bin/env python3
"""
Example: Get user's trading history

This script demonstrates how to fetch a user's trade history
including buy/sell trades, prices, sizes, and timestamps.

Usage:
    python get_user_trades.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839
    python get_user_trades.py --address 0x... --limit 100
    python get_user_trades.py --address 0x... --side BUY
"""

import requests
import argparse
import sys
from datetime import datetime
from utils import format_address


def get_user_trades(address, limit=50, side=None, market=None):
    """
    Get user's trade history.
    
    Args:
        address (str): Ethereum wallet address
        limit (int): Number of trades to return (max: 10000)
        side (str): Filter by BUY or SELL (None = both)
        market (str): Filter by condition ID (optional)
    
    Returns:
        list: User's trades
    """
    url = "https://data-api.polymarket.com/trades"
    params = {
        "user": format_address(address),
        "limit": limit
    }
    
    if side:
        params["side"] = side.upper()
    
    if market:
        params["market"] = market
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trades: {e}")
        return None


def format_timestamp(timestamp):
    """Convert Unix timestamp to readable date"""
    if timestamp:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return "N/A"


def main():
    parser = argparse.ArgumentParser(description="Get Polymarket user trading history")
    parser.add_argument(
        "--address",
        type=str,
        required=True,
        help="Wallet address (0x...)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max trades to fetch (default: 50, max: 10000)"
    )
    parser.add_argument(
        "--side",
        type=str,
        default=None,
        choices=["BUY", "SELL", "buy", "sell"],
        help="Filter by trade side (BUY or SELL)"
    )
    args = parser.parse_args()
    
    try:
        formatted_address = format_address(args.address)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    side_filter = args.side.upper() if args.side else None
    filter_text = f" ({side_filter} only)" if side_filter else ""
    
    print(f"📈 Trading History for {formatted_address}{filter_text}")
    print("=" * 100)
    print()
    
    trades = get_user_trades(args.address, args.limit, side_filter)
    
    if not trades:
        print("No trades found or error occurred.")
        return
    
    if not isinstance(trades, list) or len(trades) == 0:
        print("No trading history.")
        return
    
    # Calculate stats
    buys = [t for t in trades if t.get('side') == 'BUY']
    sells = [t for t in trades if t.get('side') == 'SELL']
    total_buy_volume = sum(t.get('size', 0) * t.get('price', 0) for t in buys)
    total_sell_volume = sum(t.get('size', 0) * t.get('price', 0) for t in sells)
    
    print(f"Total Trades: {len(trades)}")
    print(f"Buys: {len(buys)} (${total_buy_volume:,.2f})")
    print(f"Sells: {len(sells)} (${total_sell_volume:,.2f})")
    print()
    print("=" * 100)
    
    for i, trade in enumerate(trades, 1):
        side = trade.get('side', 'UNKNOWN')
        side_emoji = "🟢" if side == "BUY" else "🔴"
        
        print(f"\n{i}. {side_emoji} {side}: {trade['title']}")
        print(f"   Market: {trade.get('slug', 'N/A')}")
        print(f"   Outcome: {trade.get('outcome', 'N/A')}")
        
        # Trade details
        size = trade.get('size', 0)
        price = trade.get('price', 0)
        total_value = size * price
        
        print(f"\n   Size: {size:,.2f} shares")
        print(f"   Price: ${price:.4f}")
        print(f"   Total: ${total_value:,.2f}")
        
        # Timestamp
        timestamp = trade.get('timestamp')
        if timestamp:
            print(f"   Time: {format_timestamp(timestamp)}")
        
        # Transaction hash
        tx_hash = trade.get('transactionHash')
        if tx_hash:
            print(f"   TX: {tx_hash[:10]}...{tx_hash[-8:]}")
        
        # Trader info (if available)
        username = trade.get('name') or trade.get('pseudonym')
        if username:
            print(f"   Trader: {username}")


if __name__ == "__main__":
    main()
