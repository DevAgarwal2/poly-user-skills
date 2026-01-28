#!/usr/bin/env python3
"""
Example: Get user's portfolio value

This script demonstrates how to fetch the total value of a user's
current positions across all markets.

Usage:
    python get_portfolio_value.py --address 0x56687bf447db6ffa42ffe2204a05edaa20f55839
"""

import requests
import argparse
import sys
from utils import format_address


def get_portfolio_value(address):
    """
    Get total value of user's positions.
    
    Args:
        address (str): Ethereum wallet address
    
    Returns:
        float: Total portfolio value in USDC
    """
    url = "https://data-api.polymarket.com/value"
    params = {"user": format_address(address)}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Response is an array with one object
        if isinstance(data, list) and len(data) > 0:
            return data[0].get('value', 0)
        return 0
    except requests.exceptions.RequestException as e:
        print(f"Error fetching portfolio value: {e}")
        return None


def get_user_positions_count(address):
    """Get count of user's active positions"""
    url = "https://data-api.polymarket.com/positions"
    params = {
        "user": format_address(address),
        "limit": 1  # Just to check if positions exist
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        positions = response.json()
        return len(positions) if isinstance(positions, list) else 0
    except:
        return 0


def get_markets_traded_count(address):
    """Get number of markets user has traded"""
    url = "https://data-api.polymarket.com/traded"
    params = {"user": format_address(address)}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('traded', 0)
    except:
        return 0


def main():
    parser = argparse.ArgumentParser(description="Get Polymarket portfolio value")
    parser.add_argument(
        "--address",
        type=str,
        required=True,
        help="Wallet address (0x...)"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed stats (positions count, markets traded)"
    )
    args = parser.parse_args()
    
    try:
        formatted_address = format_address(args.address)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print(f"💰 Portfolio for {formatted_address}")
    print("=" * 80)
    print()
    
    # Get portfolio value
    value = get_portfolio_value(args.address)
    
    if value is None:
        print("Error fetching portfolio value.")
        return
    
    print(f"Total Portfolio Value: ${value:,.2f}")
    
    if args.detailed:
        print("\nFetching additional stats...")
        
        # Get positions count
        positions_count = get_user_positions_count(args.address)
        print(f"Active Positions: {positions_count}")
        
        # Get markets traded
        markets_count = get_markets_traded_count(args.address)
        print(f"Markets Traded: {markets_count}")
        
        # Calculate average position size
        if positions_count > 0:
            avg_position = value / positions_count
            print(f"Average Position Size: ${avg_position:,.2f}")
    
    print("\nNote: Value represents current market value of all positions.")
    print("Use --detailed flag for more statistics.")


if __name__ == "__main__":
    main()
