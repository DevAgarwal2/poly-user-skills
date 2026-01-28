"""
Utility functions for Polymarket Data API examples

This module provides shared helper functions used across
all Data API example scripts.
"""


def format_address(address):
    """
    Format and validate Ethereum wallet address.
    
    Polymarket Data API requires addresses to be:
    - Lowercase
    - 0x-prefixed
    - Exactly 42 characters (0x + 40 hex)
    
    Args:
        address (str): Wallet address in any format
    
    Returns:
        str: Properly formatted address
    
    Raises:
        ValueError: If address is invalid
    
    Examples:
        >>> format_address("0xABC123...")
        '0xabc123...'
        
        >>> format_address("abc123...")
        '0xabc123...'
    """
    if not address:
        raise ValueError("Address is required")
    
    # Remove 0x prefix if present, then convert to lowercase
    clean = address.lower().replace('0x', '')
    
    # Validate length
    if len(clean) != 40:
        raise ValueError(
            f"Invalid address length: {len(clean)} characters "
            f"(expected 40, got {len(clean) + 2} with 0x prefix)"
        )
    
    # Validate hex characters
    if not all(c in '0123456789abcdef' for c in clean):
        raise ValueError("Address contains invalid hex characters")
    
    # Return with 0x prefix
    return f"0x{clean}"


def format_condition_id(condition_id):
    """
    Format and validate market condition ID.
    
    Condition IDs must be:
    - Lowercase
    - 0x-prefixed
    - Exactly 66 characters (0x + 64 hex)
    
    Args:
        condition_id (str): Condition ID in any format
    
    Returns:
        str: Properly formatted condition ID
    
    Raises:
        ValueError: If condition ID is invalid
    """
    if not condition_id:
        raise ValueError("Condition ID is required")
    
    # Remove 0x prefix if present, then convert to lowercase
    clean = condition_id.lower().replace('0x', '')
    
    # Validate length
    if len(clean) != 64:
        raise ValueError(
            f"Invalid condition ID length: {len(clean)} characters "
            f"(expected 64, got {len(clean) + 2} with 0x prefix)"
        )
    
    # Validate hex characters
    if not all(c in '0123456789abcdef' for c in clean):
        raise ValueError("Condition ID contains invalid hex characters")
    
    # Return with 0x prefix
    return f"0x{clean}"


def format_pnl(pnl):
    """
    Format P&L value for display with color indicator.
    
    Args:
        pnl (float): Profit and loss value
    
    Returns:
        str: Formatted P&L string with symbol
    """
    if pnl > 0:
        return f"+${pnl:,.2f} 📈"
    elif pnl < 0:
        return f"-${abs(pnl):,.2f} 📉"
    else:
        return f"${pnl:,.2f}"


def format_percentage(percent):
    """
    Format percentage for display with color indicator.
    
    Args:
        percent (float): Percentage value
    
    Returns:
        str: Formatted percentage with symbol
    """
    if percent > 0:
        return f"+{percent:.2f}% 📈"
    elif percent < 0:
        return f"{percent:.2f}% 📉"
    else:
        return f"{percent:.2f}%"


# Example wallet addresses for testing (replace with real addresses)
EXAMPLE_ADDRESSES = {
    "trader1": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
    # Add more example addresses as needed
}


# Example condition IDs for testing (replace with real condition IDs)
EXAMPLE_CONDITION_IDS = {
    "market1": "0xdd22472e552920b8438158ea7238bfadfa4f736aa4cee91a6b86c39ead110917",
    # Add more example condition IDs as needed
}
