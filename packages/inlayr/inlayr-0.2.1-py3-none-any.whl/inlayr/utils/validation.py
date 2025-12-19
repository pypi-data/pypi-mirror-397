"""
Input validation utilities for inlayr.

Provides validation functions for common inputs like token addresses,
amounts, slippage values, and chain parameters.
"""

from __future__ import annotations

from typing import Optional


class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass


def validate_token_address(address: str, chain: str = "any") -> None:
    """
    Validate token address format.
    
    Args:
        address: Token address or mint to validate
        chain: Chain type ("evm", "solana", or "any")
        
    Raises:
        ValidationError: If address format is invalid
    """
    # Runtime type check - type hints don't enforce types at runtime
    if not address or not isinstance(address, str):
        raise ValidationError("Token address must be a non-empty string")
    
    address = address.strip()
    
    if chain == "evm":
        # EVM addresses: 0x followed by 40 hex characters
        if not address.startswith("0x") or len(address) != 42:
            raise ValidationError(
                f"Invalid EVM token address: {address}. "
                "Expected format: 0x followed by 40 hex characters"
            )
        try:
            int(address[2:], 16)
        except ValueError:
            raise ValidationError(f"Invalid EVM token address: {address}. Contains non-hex characters")
    
    elif chain == "solana":
        # Solana addresses: base58 encoded, typically 32-44 characters
        if len(address) < 32 or len(address) > 44:
            raise ValidationError(
                f"Invalid Solana token address: {address}. "
                "Expected length between 32-44 characters"
            )
        # Basic base58 character set check
        valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
        if not all(c in valid_chars for c in address):
            raise ValidationError(
                f"Invalid Solana token address: {address}. "
                "Contains invalid base58 characters"
            )


def validate_amount(amount: int, min_amount: int = 1, max_amount: Optional[int] = None) -> None:
    """
    Validate token amount.
    
    Args:
        amount: Amount in smallest unit (wei, lamports, etc.)
        min_amount: Minimum allowed amount (default: 1)
        max_amount: Maximum allowed amount (optional)
        
    Raises:
        ValidationError: If amount is invalid
    """
    # Runtime type check - type hints don't enforce types at runtime
    if not isinstance(amount, int):
        raise ValidationError(f"Amount must be an integer, got {type(amount).__name__}")
    
    if amount < min_amount:
        raise ValidationError(f"Amount must be at least {min_amount}, got {amount}")
    
    if max_amount is not None and amount > max_amount:
        raise ValidationError(f"Amount must not exceed {max_amount}, got {amount}")


def validate_slippage(slippage: int, max_slippage: int = 10000) -> None:
    """
    Validate slippage tolerance in basis points.
    
    Args:
        slippage: Slippage in basis points (100 = 1%)
        max_slippage: Maximum allowed slippage in bps (default: 10000 = 100%)
        
    Raises:
        ValidationError: If slippage is invalid
    """
    # Runtime type check - type hints don't enforce types at runtime
    if not isinstance(slippage, int):
        raise ValidationError(f"Slippage must be an integer (basis points), got {type(slippage).__name__}")
    
    if slippage < 0:
        raise ValidationError(f"Slippage cannot be negative, got {slippage}")
    
    if slippage > max_slippage:
        raise ValidationError(
            f"Slippage {slippage} bps ({slippage/100}%) exceeds maximum {max_slippage} bps ({max_slippage/100}%)"
        )


def validate_chain_id(chain_id: int, supported_chains: dict[int, str]) -> None:
    """
    Validate chain ID is supported.
    
    Args:
        chain_id: Numeric chain ID
        supported_chains: Dictionary mapping chain IDs to names
        
    Raises:
        ValidationError: If chain_id is not supported
    """
    # Runtime type check - type hints don't enforce types at runtime
    if not isinstance(chain_id, int):
        raise ValidationError(f"Chain ID must be an integer, got {type(chain_id).__name__}")
    
    if chain_id not in supported_chains:
        supported_ids = sorted(supported_chains.keys())
        raise ValidationError(
            f"Unsupported chain_id: {chain_id}. "
            f"Supported chain IDs: {supported_ids}"
        )
