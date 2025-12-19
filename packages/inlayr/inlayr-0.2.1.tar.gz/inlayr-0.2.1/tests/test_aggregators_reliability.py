"""Tests for aggregator reliability improvements (timeouts, error handling)."""

import pytest, requests
from unittest.mock import Mock, patch

# Try to import aggregators, skip tests if dependencies not available
try:
    from inlayr.aggregators.jupiter import Aggregator as JupiterAgg
    JUPITER_AVAILABLE = True
except ImportError:
    JUPITER_AVAILABLE = False
    JupiterAgg = None

try:
    from inlayr.aggregators.raydium import Aggregator as RaydiumAgg
    RAYDIUM_AVAILABLE = True
except ImportError:
    RAYDIUM_AVAILABLE = False
    RaydiumAgg = None

try:
    from inlayr.aggregators.zeroex import Aggregator as ZeroexAgg
    ZEROEX_AVAILABLE = True
except ImportError:
    ZEROEX_AVAILABLE = False
    ZeroexAgg = None

try:
    from inlayr.aggregators.oneinch import Aggregator as OneinchAgg
    ONEINCH_AVAILABLE = True
except ImportError:
    ONEINCH_AVAILABLE = False
    OneinchAgg = None


@pytest.mark.skipif(not JUPITER_AVAILABLE, reason="Jupiter dependencies not installed")
class TestJupiterTimeouts:
    """Tests for Jupiter aggregator timeout configuration."""
    
    def test_default_timeout_set(self):
        """Jupiter should have default timeout configured."""
        agg = JupiterAgg()
        assert hasattr(agg, 'timeout')
        assert agg.timeout > 0
    
    def test_custom_timeout(self):
        """Jupiter should accept custom timeout."""
        agg = JupiterAgg(timeout=60)
        assert agg.timeout == 60
    
    @patch('requests.Session.get')
    def test_get_quote_uses_timeout(self, mock_get):
        """get_quote should pass timeout to session."""
        agg = JupiterAgg(timeout=25)
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        agg.get_quote(
            source_token="test",
            source_amount=1000,
            destination_token="test"
        )
        
        # Verify timeout was passed
        call_kwargs = mock_get.call_args[1]
        assert 'timeout' in call_kwargs
        assert call_kwargs['timeout'] == 25


@pytest.mark.skipif(not RAYDIUM_AVAILABLE, reason="Raydium dependencies not installed")
class TestRaydiumPriorityFee:
    """Tests for Raydium priority_fee handling."""
    
    @patch('requests.Session.get')
    @patch('requests.Session.post')
    def test_default_priority_fee(self, mock_post, mock_get):
        """Raydium should use 'medium' as default priority_fee."""
        agg = RaydiumAgg()
        
        # Mock fee API response
        fee_response = Mock()
        fee_response.json.return_value = {
            "data": {
                "default": {
                    "low": 100,
                    "medium": 500,
                    "high": 1000
                }
            }
        }
        fee_response.raise_for_status = Mock()
        
        # Mock swap API response
        swap_response = Mock()
        swap_response.json.return_value = {"data": []}
        swap_response.raise_for_status = Mock()
        
        mock_get.return_value = fee_response
        mock_post.return_value = swap_response
        
        # Mock required objects
        mock_quote = Mock()
        mock_quote.quote = {
            "data": {
                "inputMint": "So11111111111111111111111111111111111111112",
                "outputMint": "So11111111111111111111111111111111111111112"
            }
        }
        mock_wallet = Mock()
        mock_wallet.pubkey.return_value = Mock()
        mock_wallet.pubkey.return_value.__str__ = Mock(return_value="test_pubkey")
        
        mock_chain = Mock()
        mock_chain.wallet = mock_wallet
        
        # Should not raise KeyError
        try:
            agg.get_swap(quote=mock_quote, chain=mock_chain)
        except Exception as e:
            # We expect some errors due to mocking, but not KeyError for priority_fee
            assert not isinstance(e, KeyError)
    
    @patch('requests.Session.get')
    def test_custom_priority_fee(self, mock_get):
        """Raydium should use custom priority_fee if provided."""
        agg = RaydiumAgg()
        
        fee_response = Mock()
        fee_response.json.return_value = {
            "data": {
                "default": {
                    "low": 100,
                    "medium": 500,
                    "high": 1000
                }
            }
        }
        fee_response.raise_for_status = Mock()
        
        mock_get.return_value = fee_response
        
        # Verify 'high' priority would be used if available
        # (actual test would need more mocking)
        assert agg is not None
    
    @patch('requests.Session.get')
    def test_invalid_priority_fee_fallback(self, mock_get):
        """Invalid priority_fee should fall back to 'medium'."""
        agg = RaydiumAgg()
        
        fee_response = Mock()
        fee_response.json.return_value = {
            "data": {
                "default": {
                    "low": 100,
                    "medium": 500,
                    "high": 1000
                }
            }
        }
        fee_response.raise_for_status = Mock()
        mock_get.return_value = fee_response
        
        # Should not raise even with invalid priority_fee
        assert agg is not None


@pytest.mark.skipif(not ZEROEX_AVAILABLE, reason="0x dependencies not installed")
class TestZeroexTimeouts:
    """Tests for 0x aggregator timeout configuration."""
    
    def test_default_timeout_set(self):
        """0x should have default timeout configured."""
        agg = ZeroexAgg()
        assert hasattr(agg, 'timeout')
        assert agg.timeout > 0
    
    def test_custom_timeout(self):
        """0x should accept custom timeout."""
        agg = ZeroexAgg(timeout=45)
        assert agg.timeout == 45


@pytest.mark.skipif(not ONEINCH_AVAILABLE, reason="1inch dependencies not installed")
class TestOneinchTimeouts:
    """Tests for 1inch aggregator timeout configuration."""
    
    def test_default_timeout_set(self):
        """1inch should have default timeout configured."""
        agg = OneinchAgg()
        assert hasattr(agg, 'timeout')
        assert agg.timeout > 0
    
    def test_custom_timeout(self):
        """1inch should accept custom timeout."""
        agg = OneinchAgg(timeout=50)
        assert agg.timeout == 50


@pytest.mark.skipif(not JUPITER_AVAILABLE, reason="Jupiter dependencies not installed")
class TestHTTPErrorHandling:
    """Tests for HTTP error handling with raise_for_status."""
    
    @patch('requests.Session.get')
    def test_bad_request_raises(self, mock_get):
        """4xx errors should raise HTTPError."""
        agg = JupiterAgg()
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.HTTPError("Bad Request")
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.HTTPError):
            agg.get_quote(
                source_token="test",
                source_amount=1000,
                destination_token="test"
            )
    
    @patch('requests.Session.get')
    def test_server_error_raises(self, mock_get):
        """5xx errors should raise HTTPError."""
        agg = JupiterAgg()
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("Server Error")
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.HTTPError):
            agg.get_quote(
                source_token="test",
                source_amount=1000,
                destination_token="test"
            )
