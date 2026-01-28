#!/usr/bin/env python3
"""
Example: Get user's complete activity history

This script demonstrates how to fetch a user's complete activity history,
including trades, splits, merges, redeems, rewards, and more.

The /activity endpoint is more comprehensive than /trades - it includes:
  - TRADE (buy/sell)
  - SPLIT (splitting outcome tokens)
  - MERGE (merging outcome tokens)
  - REDEEM (redeeming winning tokens)
  - REWARD (trading rewards)
  - CONVERSION (token conversions)
  - MAKER_REBATE (maker rebate bonuses)

Usage:
    python get_user_activity.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839
    python get_user_activity.py --address 0x... --limit 100
    python get_user_activity.py --address 0x... --type TRADE,REDEEM
    python get_user_activity.py --address 0x... --side BUY
"""

import requests
import argparse
import sys
from datetime import datetime
from utils import format_address


def get_user_activity(
    address,
    limit=50,
    offset=0,
    activity_types=None,
    side=None,
    sort_by="TIMESTAMP",
    sort_direction="DESC"
):
    """
    Get user's complete activity history.
    
    Args:
        address (str): Ethereum wallet address
        limit (int): Number of activities to return (max: 500)
        offset (int): Pagination offset
        activity_types (list): Filter by types: TRADE, SPLIT, MERGE, REDEEM, REWARD, CONVERSION, MAKER_REBATE
        side (str): Filter trades by BUY or SELL
        sort_by (str): Sort field - TIMESTAMP, TOKENS, CASH
        sort_direction (str): ASC or DESC
    
    Returns:
        list: User's activity with transaction details
    """
    url = "https://data-api.polymarket.com/activity"
    params = {
        "user": format_address(address),
        "limit": limit,
        "offset": offset,
        "sortBy": sort_by,
        "sortDirection": sort_direction
    }
    
    if activity_types:
        params["type"] = ",".join(activity_types)
    
    if side:
        params["side"] = side
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching activity: {e}")
        return None


def format_activity_type(activity_type):
    """Format activity type with emoji"""
    type_emojis = {
        "TRADE": "📊",
        "SPLIT": "✂️",
        "MERGE": "🔗",
        "REDEEM": "💰",
        "REWARD": "🎁",
        "CONVERSION": "🔄",
        "MAKER_REBATE": "💵"
    }
    emoji = type_emojis.get(activity_type, "📌")
    return f"{emoji} {activity_type}"


def display_activity(activities):
    """Display activity in a readable format"""
    if not activities or len(activities) == 0:
        print("No activity found.")
        return
    
    # Group by type
    type_counts = {}
    total_volume = 0
    
    for activity in activities:
        activity_type = activity.get('type', 'UNKNOWN')
        type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
        
        # Calculate volume for trades
        if activity_type == 'TRADE':
            size = activity.get('size', 0)
            price = activity.get('price', 0)
            total_volume += size * price
    
    print(f"\n📊 Activity Summary")
    print("-" * 100)
    print(f"Total Activities: {len(activities)}")
    print(f"\nBreakdown by Type:")
    for activity_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {format_activity_type(activity_type)}: {count}")
    
    if total_volume > 0:
        print(f"\nTotal Trade Volume: ${total_volume:,.2f}")
    
    print("\n" + "=" * 100)
    print("ACTIVITY HISTORY")
    print("=" * 100)
    
    for i, activity in enumerate(activities, 1):
        activity_type = activity.get('type', 'UNKNOWN')
        timestamp = activity.get('timestamp')
        time_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'
        
        print(f"\n{i}. {format_activity_type(activity_type)} | {time_str}")
        
        # Common fields
        title = activity.get('title', 'Unknown market')
        print(f"   Market: {title[:70]}")
        
        if activity.get('outcome'):
            print(f"   Outcome: {activity.get('outcome')}")
        
        # Type-specific details
        if activity_type == 'TRADE':
            side = activity.get('side', 'N/A')
            side_emoji = "🟢" if side == "BUY" else "🔴"
            size = activity.get('size', 0)
            price = activity.get('price', 0)
            value = size * price
            
            print(f"   {side_emoji} {side}: {size:,.2f} shares @ ${price:.4f}")
            print(f"   Value: ${value:,.2f}")
        
        elif activity_type in ['SPLIT', 'MERGE']:
            size = activity.get('size', 0)
            usdc_size = activity.get('usdcSize', 0)
            print(f"   Tokens: {size:,.2f}")
            print(f"   USDC: ${usdc_size:,.2f}")
        
        elif activity_type == 'REDEEM':
            size = activity.get('size', 0)
            usdc_size = activity.get('usdcSize', 0)
            print(f"   Redeemed: {size:,.2f} tokens")
            print(f"   Received: ${usdc_size:,.2f} USDC")
        
        elif activity_type in ['REWARD', 'MAKER_REBATE']:
            usdc_size = activity.get('usdcSize', 0)
            print(f"   Amount: ${usdc_size:,.2f}")
        
        # Transaction hash (if available)
        tx_hash = activity.get('transactionHash')
        if tx_hash:
            print(f"   TX: {tx_hash[:10]}...{tx_hash[-8:]}")
        
        # Add separator every 5 items for readability
        if i % 5 == 0 and i < len(activities):
            print("   " + "-" * 95)


def main():
    parser = argparse.ArgumentParser(description="Get Polymarket user activity")
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
        help="Max activities to fetch (default: 50, max: 500)"
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Pagination offset (default: 0)"
    )
    parser.add_argument(
        "--type",
        type=str,
        help="Filter by types (comma-separated): TRADE,SPLIT,MERGE,REDEEM,REWARD,CONVERSION,MAKER_REBATE"
    )
    parser.add_argument(
        "--side",
        type=str,
        choices=["BUY", "SELL"],
        help="Filter trades by side (BUY or SELL)"
    )
    parser.add_argument(
        "--sort",
        type=str,
        default="TIMESTAMP",
        choices=["TIMESTAMP", "TOKENS", "CASH"],
        help="Sort by field (default: TIMESTAMP)"
    )
    parser.add_argument(
        "--direction",
        type=str,
        default="DESC",
        choices=["ASC", "DESC"],
        help="Sort direction (default: DESC)"
    )
    args = parser.parse_args()
    
    try:
        formatted_address = format_address(args.address)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Parse activity types
    activity_types = None
    if args.type:
        activity_types = [t.strip().upper() for t in args.type.split(',')]
    
    print(f"🔍 Fetching activity for {formatted_address}...")
    
    if args.type:
        print(f"   Filter: {', '.join(activity_types)}")
    if args.side:
        print(f"   Side: {args.side}")
    
    activities = get_user_activity(
        args.address,
        args.limit,
        args.offset,
        activity_types,
        args.side,
        args.sort,
        args.direction
    )
    
    if not activities:
        print("No activities found or error occurred.")
        return
    
    display_activity(activities)
    
    # Pagination hint
    if len(activities) >= args.limit:
        print(f"\n💡 Tip: There may be more activities. Use --offset {args.offset + args.limit} to see more.")


if __name__ == "__main__":
    main()
