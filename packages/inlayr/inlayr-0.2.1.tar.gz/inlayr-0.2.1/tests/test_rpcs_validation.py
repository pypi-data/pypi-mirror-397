"""Tests for RPC chain_id validation."""

import pytest
from inlayr.utils.validation import ValidationError

# Try to import RPCs, skip tests if dependencies not available
try:
    from inlayr.rpcs.onerpc import RPC as OneRPC
    ONERPC_AVAILABLE = True
except ImportError:
    ONERPC_AVAILABLE = False
    OneRPC = None

try:
    from inlayr.rpcs.ankr import RPC as AnkrRPC
    ANKR_AVAILABLE = True
except ImportError:
    ANKR_AVAILABLE = False
    AnkrRPC = None


@pytest.mark.skipif(not ONERPC_AVAILABLE, reason="1RPC dependencies (web3) not installed")
class TestOneRPCValidation:
    """Tests for 1RPC chain_id validation."""
    
    def test_valid_chain_id(self):
        """Valid chain_id should initialize successfully."""
        rpc = OneRPC(chain_id=1)  # Ethereum mainnet
        assert rpc.chain_id == 1
        assert rpc.name == "1rpc"
    
    def test_another_valid_chain(self):
        """Another valid chain should work."""
        rpc = OneRPC(chain_id=137)  # Polygon
        assert rpc.chain_id == 137
    
    def test_invalid_chain_id_raises(self):
        """Invalid chain_id should raise ValidationError."""
        with pytest.raises(ValidationError, match="Unsupported chain_id: 99999"):
            OneRPC(chain_id=99999)
    
    def test_error_message_helpful(self):
        """Error message should list supported chains."""
        with pytest.raises(ValidationError, match="Supported chain IDs"):
            OneRPC(chain_id=12345)


@pytest.mark.skipif(not ANKR_AVAILABLE, reason="Ankr dependencies (web3) not installed")
class TestAnkrRPCValidation:
    """Tests for Ankr RPC chain_id validation."""
    
    def test_valid_chain_id(self):
        """Valid chain_id should initialize successfully."""
        rpc = AnkrRPC(chain_id=1, api_key="test_key")
        assert rpc.chain_id == 1
        assert rpc.name == "ankr"
    
    def test_another_valid_chain(self):
        """Another valid chain should work."""
        rpc = AnkrRPC(chain_id=56, api_key="test_key")  # BSC
        assert rpc.chain_id == 56
    
    def test_invalid_chain_id_raises(self):
        """Invalid chain_id should raise ValidationError."""
        with pytest.raises(ValidationError, match="Unsupported chain_id: 77777"):
            AnkrRPC(chain_id=77777, api_key="test_key")
    
    def test_error_message_helpful(self):
        """Error message should list supported chains."""
        with pytest.raises(ValidationError, match="Supported chain IDs"):
            AnkrRPC(chain_id=88888, api_key="test_key")


@pytest.mark.skipif(not (ONERPC_AVAILABLE and ANKR_AVAILABLE), reason="RPC dependencies not installed")
class TestRPCURLConstruction:
    """Tests that URLs are constructed correctly after validation."""
    
    def test_onerpc_url_format(self):
        """1RPC URL should be correctly formatted."""
        rpc = OneRPC(chain_id=1)
        assert rpc.rpc_url == "https://1rpc.io/eth"
    
    def test_ankr_url_format(self):
        """Ankr URL should be correctly formatted."""
        rpc = AnkrRPC(chain_id=1, api_key="my_api_key")
        assert rpc.rpc_url == "https://rpc.ankr.com/eth/my_api_key"
        assert "my_api_key" in rpc.rpc_url
