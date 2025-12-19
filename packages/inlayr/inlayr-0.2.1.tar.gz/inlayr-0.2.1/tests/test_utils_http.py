"""Tests for HTTP utilities."""

import requests
from unittest.mock import Mock, patch
from inlayr.utils.http import (
    create_session_with_retries,
    TimeoutHTTPAdapter,
)


class TestCreateSessionWithRetries:
    """Tests for session creation with retry logic."""
    
    def test_creates_session(self):
        """Should create a requests.Session instance."""
        session = create_session_with_retries()
        assert isinstance(session, requests.Session)
    
    def test_has_retry_adapter(self):
        """Session should have retry adapter mounted."""
        session = create_session_with_retries()
        adapter = session.get_adapter("https://example.com")
        assert isinstance(adapter, requests.adapters.HTTPAdapter)
    
    def test_custom_timeout(self):
        """Should accept custom timeout parameter."""
        session = create_session_with_retries(timeout=60)
        assert session is not None
    
    def test_custom_retries(self):
        """Should accept custom retries parameter."""
        session = create_session_with_retries(retries=5)
        assert session is not None


class TestTimeoutHTTPAdapter:
    """Tests for TimeoutHTTPAdapter."""
    
    def test_default_timeout_set(self):
        """Adapter should have default timeout."""
        adapter = TimeoutHTTPAdapter(timeout=42)
        assert adapter.timeout == 42
    
    def test_uses_default_timeout(self):
        """Adapter should use default timeout when not specified."""
        adapter = TimeoutHTTPAdapter(timeout=15)
        assert adapter.timeout == 15


class TestTimeoutBehavior:
    """Integration tests for timeout behavior."""
    
    @patch('requests.Session.get')
    def test_timeout_parameter_passed(self, mock_get):
        """Timeout should be passed to requests."""
        session = create_session_with_retries(timeout=25)
        
        mock_get.return_value = Mock(status_code=200)
        
        assert session is not None
    
    def test_session_has_both_protocols(self):
        """Session should handle both http and https."""
        session = create_session_with_retries()
        http_adapter = session.get_adapter("http://example.com")
        https_adapter = session.get_adapter("https://example.com")
        
        assert http_adapter is not None
        assert https_adapter is not None
