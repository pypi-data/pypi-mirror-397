"""
HTTP utilities for reliable network requests.

Provides session configuration with timeouts and retry logic.
"""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_RETRIES = 3


def create_session_with_retries(
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    backoff_factor: float = 1.0,
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
) -> requests.Session:
    """
    Create a requests Session with automatic retries and timeout.
    
    Args:
        timeout: Request timeout in seconds (default: 30)
        retries: Maximum number of retry attempts (default: 3)
        backoff_factor: Backoff multiplier for retries (default: 1.0)
            Retry delays: {backoff factor} * (2 ** ({retry number} - 1))
        status_forcelist: HTTP status codes that trigger retries
            
    Returns:
        Configured requests.Session instance
        
    Example:
        >>> session = create_session_with_retries(timeout=30, retries=3)
        >>> response = session.get("https://api.example.com/quote")
    """
    session = requests.Session()
    
    retry_strategy = Retry(
        total=retries,
        status_forcelist=status_forcelist,
        backoff_factor=backoff_factor,
        allowed_methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


class TimeoutHTTPAdapter(HTTPAdapter):
    """HTTP adapter that adds default timeout to all requests."""
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, *args, **kwargs):
        self.timeout = timeout
        super().__init__(*args, **kwargs)
    
    def send(self, request, **kwargs):
        """Add default timeout if not specified."""
        kwargs.setdefault("timeout", self.timeout)
        return super().send(request, **kwargs)
