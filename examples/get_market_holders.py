#!/usr/bin/env python3
"""
Example: Get top holders for a market

This script demonstrates how to fetch the top position holders
for a specific market by condition ID.

Usage:
    python get_market_holders.py --market 0xdd22472e552920b8438158ea7238bfadfa4f736aa4cee91a6b86c39ead110917
    python get_market_holders.py --market 0x... --limit 20
"""

import requests
import argparse
import sys
from utils import format_condition_id


def get_market_holders(condition_id, limit=10):
    """
    Get top holders for a market.
    
    Args:
        condition_id (str): Market condition ID (0x... 66 chars)
        limit (int): Number of holders per token (max: 20)
    
    Returns:
        list: Top holders data
    """
    url = "https://data-api.polymarket.com/holders"
    params = {
        "market": format_condition_id(condition_id),
        "limit": min(limit, 20)
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching holders: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Get top holders for a Polymarket market")
    parser.add_argument(
        "--market",
        type=str,
        required=True,
        help="Market condition ID (0x... 66 chars)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max holders per outcome (default: 10, max: 20)"
    )
    args = parser.parse_args()
    
    try:
        formatted_id = format_condition_id(args.market)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print(f"👥 Top Holders for Market")
    print(f"Condition ID: {formatted_id}")
    print("=" * 100)
    print()
    
    holders_data = get_market_holders(args.market, args.limit)
    
    if not holders_data:
        print("No holders data found or error occurred.")
        return
    
    if not isinstance(holders_data, list) or len(holders_data) == 0:
        print("No holders found.")
        return
    
    # Each item in the array represents a token (outcome)
    for token_data in holders_data:
        token = token_data.get('token', 'Unknown')
        holders = token_data.get('holders', [])
        
        if not holders:
            continue
        
        # Try to determine outcome from first holder
        outcome = holders[0].get('outcomeIndex', 0)
        outcome_name = "Yes" if outcome == 0 else "No"
        
        print(f"\n{outcome_name} Holders (Token: {token[:10]}...{token[-8:]})")
        print("-" * 100)
        
        # Calculate total position
        total_amount = sum(h.get('amount', 0) for h in holders)
        
        for i, holder in enumerate(holders, 1):
            amount = holder.get('amount', 0)
            percentage = (amount / total_amount * 100) if total_amount > 0 else 0
            
            # User info
            username = holder.get('name') or holder.get('pseudonym', 'Anonymous')
            wallet = holder.get('proxyWallet', 'Unknown')
            
            print(f"\n{i:2d}. {username}")
            print(f"    Wallet: {wallet}")
            print(f"    Amount: {amount:,.2f} shares ({percentage:.2f}% of {outcome_name})")
            
            # Bio
            bio = holder.get('bio')
            if bio:
                bio_short = bio[:80] + "..." if len(bio) > 80 else bio
                print(f"    Bio: {bio_short}")
            
            # Display username setting
            if holder.get('displayUsernamePublic'):
                print(f"    Public Profile: ✓")
        
        print(f"\nTotal {outcome_name} shares tracked: {total_amount:,.2f}")
    
    print("\n" + "=" * 100)
    print("Note: Only shows top holders. Total may not represent entire market.")


if __name__ == "__main__":
    main()
