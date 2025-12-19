"""Tests for input validation utilities."""

import pytest
from inlayr.utils.validation import (
    ValidationError,
    validate_token_address,
    validate_amount,
    validate_slippage,
    validate_chain_id,
)


class TestValidateTokenAddress:
    """Tests for token address validation."""
    
    def test_valid_evm_address(self):
        """Valid EVM address should not raise."""
        validate_token_address("0x1234567890123456789012345678901234567890", "evm")
    
    def test_invalid_evm_address_no_prefix(self):
        """EVM address without 0x prefix should raise."""
        with pytest.raises(ValidationError, match="Invalid EVM token address"):
            validate_token_address("1234567890123456789012345678901234567890", "evm")
    
    def test_invalid_evm_address_wrong_length(self):
        """EVM address with wrong length should raise."""
        with pytest.raises(ValidationError, match="Invalid EVM token address"):
            validate_token_address("0x12345", "evm")
    
    def test_invalid_evm_address_non_hex(self):
        """EVM address with non-hex characters should raise."""
        with pytest.raises(ValidationError, match="non-hex characters"):
            validate_token_address("0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG", "evm")
    
    def test_valid_solana_address(self):
        """Valid Solana address should not raise."""
        validate_token_address("So11111111111111111111111111111111111111112", "solana")
        validate_token_address("4eDf52YYzL6i6gbZ6FXqrLUPXbtP61f1gPSFM66M4XHe", "solana")
    
    def test_invalid_solana_address_too_short(self):
        """Solana address that's too short should raise."""
        with pytest.raises(ValidationError, match="Invalid Solana token address"):
            validate_token_address("short", "solana")
    
    def test_invalid_solana_address_invalid_chars(self):
        """Solana address with invalid base58 characters should raise."""
        with pytest.raises(ValidationError, match="invalid base58 characters"):
            validate_token_address("0O0O0O0O0O0O0O0O0O0O0O0O0O0O0O0O0O0O", "solana")
    
    def test_empty_address(self):
        """Empty address should raise."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_token_address("", "any")
    
    def test_non_string_address(self):
        """Non-string address should raise."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_token_address(123, "any")


class TestValidateAmount:
    """Tests for amount validation."""
    
    def test_valid_amount(self):
        """Valid amount should not raise."""
        validate_amount(1000000)
    
    def test_zero_amount_fails(self):
        """Zero amount should raise by default."""
        with pytest.raises(ValidationError, match="must be at least 1"):
            validate_amount(0)
    
    def test_negative_amount_fails(self):
        """Negative amount should raise."""
        with pytest.raises(ValidationError, match="must be at least 1"):
            validate_amount(-100)
    
    def test_custom_min_amount(self):
        """Custom minimum amount should be enforced."""
        with pytest.raises(ValidationError, match="must be at least 1000"):
            validate_amount(500, min_amount=1000)
    
    def test_max_amount_enforced(self):
        """Maximum amount should be enforced."""
        with pytest.raises(ValidationError, match="must not exceed 1000"):
            validate_amount(2000, max_amount=1000)
    
    def test_non_integer_amount(self):
        """Non-integer amount should raise."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_amount(123.45)


class TestValidateSlippage:
    """Tests for slippage validation."""
    
    def test_valid_slippage(self):
        """Valid slippage should not raise."""
        validate_slippage(100)  # 1%
        validate_slippage(1000)  # 10%
    
    def test_zero_slippage(self):
        """Zero slippage should be valid."""
        validate_slippage(0)
    
    def test_negative_slippage_fails(self):
        """Negative slippage should raise."""
        with pytest.raises(ValidationError, match="cannot be negative"):
            validate_slippage(-100)
    
    def test_excessive_slippage_fails(self):
        """Slippage exceeding maximum should raise."""
        with pytest.raises(ValidationError, match="exceeds maximum"):
            validate_slippage(15000)  # 150%
    
    def test_custom_max_slippage(self):
        """Custom maximum slippage should be enforced."""
        with pytest.raises(ValidationError, match="exceeds maximum 500"):
            validate_slippage(1000, max_slippage=500)
    
    def test_non_integer_slippage(self):
        """Non-integer slippage should raise."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_slippage(12.5)


class TestValidateChainId:
    """Tests for chain ID validation."""
    
    def test_valid_chain_id(self):
        """Valid chain ID should not raise."""
        chains = {1: "ethereum", 56: "bsc"}
        validate_chain_id(1, chains)
        validate_chain_id(56, chains)
    
    def test_invalid_chain_id_fails(self):
        """Invalid chain ID should raise with helpful message."""
        chains = {1: "ethereum", 56: "bsc"}
        with pytest.raises(ValidationError, match="Unsupported chain_id: 999"):
            validate_chain_id(999, chains)
    
    def test_error_message_includes_supported_chains(self):
        """Error message should list supported chain IDs."""
        chains = {1: "ethereum", 56: "bsc", 137: "polygon"}
        with pytest.raises(ValidationError, match=r"\[1, 56, 137\]"):
            validate_chain_id(999, chains)
    
    def test_non_integer_chain_id(self):
        """Non-integer chain ID should raise."""
        chains = {1: "ethereum"}
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_chain_id("1", chains)
