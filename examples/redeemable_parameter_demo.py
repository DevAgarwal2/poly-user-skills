#!/usr/bin/env python3
"""
Example: Understanding redeemable parameter for positions

This script demonstrates the difference between:
  1. redeemable=false → Only CURRENT active positions
  2. redeemable=true → Old positions with PAYOUTS LEFT + current ones
  3. No redeemable → ALL positions

The redeemable parameter is crucial for understanding what positions
a user has and whether they have unclaimed payouts from resolved markets.
"""

import requests
from utils import format_address


def get_positions_comparison(address):
    """
    Compare different redeemable parameter values
    
    Args:
        address (str): Wallet address to analyze
    """
    base_url = "https://data-api.polymarket.com/positions"
    formatted_addr = format_address(address)
    
    print(f"Comparing position queries for: {formatted_addr}")
    print("=" * 80)
    
    # Query 1: Active positions only (redeemable=false)
    print("\n1️⃣  ACTIVE POSITIONS ONLY (redeemable=false)")
    print("-" * 80)
    response = requests.get(
        base_url,
        params={
            "user": formatted_addr,
            "sizeThreshold": 1,
            "limit": 100,
            "sortBy": "TOKENS",
            "sortDirection": "DESC",
            "redeemable": "false"  # Only current active positions
        }
    )
    
    if response.ok:
        active = response.json()
        print(f"Found {len(active)} active position(s)")
        if active:
            total_value = sum(p.get('currentValue', 0) for p in active)
            print(f"Total value: ${total_value:,.2f}")
            print("\nSample positions:")
            for p in active[:3]:
                print(f"  - {p.get('title', 'N/A')[:60]}")
                print(f"    Value: ${p.get('currentValue', 0):,.2f}, Redeemable: {p.get('redeemable', False)}")
    else:
        print(f"Error: {response.status_code}")
    
    # Query 2: Redeemable positions (old positions with payouts)
    print("\n\n2️⃣  CLAIMABLE PAYOUTS (redeemable=true)")
    print("-" * 80)
    response = requests.get(
        base_url,
        params={
            "user": formatted_addr,
            "sizeThreshold": 1,
            "limit": 100,
            "sortBy": "TOKENS",
            "sortDirection": "DESC",
            "redeemable": "true"  # Old positions with payouts left
        }
    )
    
    if response.ok:
        redeemable = response.json()
        print(f"Found {len(redeemable)} redeemable position(s)")
        if redeemable:
            total_claimable = sum(p.get('currentValue', 0) for p in redeemable)
            print(f"Total claimable: ${total_claimable:,.2f}")
            print("\nSample redeemable positions:")
            for p in redeemable[:3]:
                print(f"  - {p.get('title', 'N/A')[:60]}")
                print(f"    Claimable: ${p.get('currentValue', 0):,.2f}, Redeemable: {p.get('redeemable', False)}")
    else:
        print(f"Error: {response.status_code}")
    
    # Query 3: ALL positions (no redeemable filter)
    print("\n\n3️⃣  ALL POSITIONS (no redeemable parameter)")
    print("-" * 80)
    response = requests.get(
        base_url,
        params={
            "user": formatted_addr,
            "sizeThreshold": 1,
            "limit": 100,
            "sortBy": "TOKENS",
            "sortDirection": "DESC"
            # No redeemable parameter = get everything
        }
    )
    
    if response.ok:
        all_positions = response.json()
        print(f"Found {len(all_positions)} total position(s)")
        if all_positions:
            total_all = sum(p.get('currentValue', 0) for p in all_positions)
            active_count = sum(1 for p in all_positions if not p.get('redeemable'))
            redeemable_count = sum(1 for p in all_positions if p.get('redeemable'))
            
            print(f"Total value: ${total_all:,.2f}")
            print(f"  - Active: {active_count}")
            print(f"  - Redeemable: {redeemable_count}")
            
            print("\nBreakdown by status:")
            for p in all_positions[:5]:
                status = "🟢 Active" if not p.get('redeemable') else "💰 Claimable"
                print(f"  {status}: {p.get('title', 'N/A')[:50]}")
                print(f"    Value: ${p.get('currentValue', 0):,.2f}")
    else:
        print(f"Error: {response.status_code}")
    
    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
When to use each parameter:

✅ redeemable=false
   → Get ONLY current active positions
   → Use for: portfolio tracking, active position management
   → Example: "Show me what I'm currently trading"

💰 redeemable=true  
   → Get positions with UNCLAIMED PAYOUTS from resolved markets
   → Use for: finding money to claim, checking old positions
   → Example: "Do I have any payouts to claim?"

🔄 No redeemable parameter (or omitted)
   → Get EVERYTHING (active + redeemable)
   → Use for: complete portfolio view
   → Example: "Show me all my positions and claimable funds"
""")


if __name__ == "__main__":
    # Example addresses (replace with actual address)
    test_addresses = [
        "0x742d35cc6634c0532925a3b844bc9e7595f0bee",
        "0x56687bf447db6ffa42ffe2204a05edaa20f55839"
    ]
    
    print("This example compares the 'redeemable' parameter behavior\n")
    
    # Use first test address or ask for input
    import sys
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        print("Usage: python redeemable_parameter_demo.py 0xYOUR_ADDRESS")
        print(f"\nUsing example address: {test_addresses[0]}")
        address = test_addresses[0]
    
    get_positions_comparison(address)
