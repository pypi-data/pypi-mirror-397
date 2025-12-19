"""
TempMailChecker Python SDK Client
"""

import re
from typing import Optional, Dict, Any
import requests
from requests.exceptions import RequestException, Timeout


# Regional endpoint URLs
# All endpoints use /check and /usage directly (no /api prefix)
ENDPOINT_EU = "https://tempmailchecker.com"
ENDPOINT_US = "https://us.tempmailchecker.com"
ENDPOINT_ASIA = "https://asia.tempmailchecker.com"

# Default base API URL (EU endpoint)
DEFAULT_ENDPOINT = ENDPOINT_EU
DEFAULT_TIMEOUT = 10  # seconds


class TempMailChecker:
    """
    TempMailChecker Python SDK
    
    Detect disposable email addresses using the TempMailChecker API.
    
    Args:
        api_key: Your TempMailChecker API key
        endpoint: Optional custom endpoint. Use constants:
                  - ENDPOINT_EU (default)
                  - ENDPOINT_US
                  - ENDPOINT_ASIA
        timeout: Request timeout in seconds (default: 10)
    
    Example:
        >>> checker = TempMailChecker('your_api_key')
        >>> is_disposable = checker.is_disposable('user@tempmail.com')
        >>> print(is_disposable)
        True
    """
    
    def __init__(
        self,
        api_key: str,
        endpoint: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT
    ):
        if not api_key or not api_key.strip():
            raise ValueError("API key is required")
        
        self.api_key = api_key.strip()
        self.endpoint = endpoint or DEFAULT_ENDPOINT
        self.timeout = timeout
    
    def set_timeout(self, seconds: int) -> "TempMailChecker":
        """
        Set request timeout.
        
        Args:
            seconds: Timeout in seconds
        
        Returns:
            Self for chaining
        """
        self.timeout = seconds
        return self
    
    def is_disposable(self, email: str) -> bool:
        """
        Check if an email address is disposable.
        
        Args:
            email: Full email address to check
        
        Returns:
            True if disposable, False if legitimate
        
        Raises:
            ValueError: If email is invalid
            RequestException: On API errors
        """
        result = self.check(email)
        return result.get("temp", False) is True
    
    def is_disposable_domain(self, domain: str) -> bool:
        """
        Check if a domain is disposable.
        
        Args:
            domain: Domain name to check (e.g., 'tempmail.com')
        
        Returns:
            True if disposable, False if legitimate
        
        Raises:
            ValueError: If domain is invalid
            RequestException: On API errors
        """
        result = self.check_domain(domain)
        return result.get("temp", False) is True
    
    def check(self, email: str) -> Dict[str, Any]:
        """
        Check an email address and return full response.
        
        Args:
            email: Full email address to check
        
        Returns:
            Response dictionary with 'temp' boolean
        
        Raises:
            ValueError: If email is invalid
            RequestException: On API errors
        """
        if not email or not email.strip():
            raise ValueError("Email address is required")
        
        email = email.strip()
        
        # Basic email validation
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email address format")
        
        url = self._get_api_url("/check")
        params = {"email": email}
        
        return self._make_request(url, params, require_auth=True)
    
    def check_domain(self, domain: str) -> Dict[str, Any]:
        """
        Check a domain and return full response.
        
        Args:
            domain: Domain name to check
        
        Returns:
            Response dictionary with 'temp' boolean
        
        Raises:
            ValueError: If domain is invalid
            RequestException: On API errors
        """
        if not domain or not domain.strip():
            raise ValueError("Domain is required")
        
        # Clean domain
        clean_domain = domain.strip()
        # Remove protocol if present
        clean_domain = re.sub(r'^https?://', '', clean_domain)
        # Remove path if present
        clean_domain = clean_domain.split('/')[0]
        # Remove port if present
        clean_domain = clean_domain.split(':')[0]
        
        url = self._get_api_url("/check")
        params = {"domain": clean_domain}
        
        return self._make_request(url, params, require_auth=True)
    
    def get_usage(self) -> Dict[str, Any]:
        """
        Get current API usage statistics.
        
        Returns:
            Usage stats dictionary with 'usage_today', 'limit', 'reset'
        
        Raises:
            RequestException: On API errors
        """
        url = self._get_api_url("/usage")
        params = {"key": self.api_key}
        
        return self._make_request(url, params, require_auth=False)
    
    def _get_api_url(self, path: str) -> str:
        """
        Get the full API URL.
        
        All endpoints use paths directly: /check, /usage (no /api prefix)
        
        Args:
            path: API endpoint path (e.g., '/check', '/usage')
        
        Returns:
            Full URL
        """
        base = self.endpoint.rstrip('/')
        return f"{base}{path}"
    
    def _make_request(
        self,
        url: str,
        params: Dict[str, str],
        require_auth: bool = True
    ) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            url: Full API URL
            params: Query parameters
            require_auth: Whether to include API key header
        
        Returns:
            Decoded JSON response
        
        Raises:
            RequestException: On API errors
        """
        headers = {}
        if require_auth:
            headers["X-API-Key"] = self.api_key
        
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 429:
                data = response.json()
                message = data.get("message", "Daily limit reached")
                raise RequestException(f"Rate limit exceeded: {message}")
            
            if not response.ok:
                data = response.json()
                error_msg = data.get("error", "API request failed")
                raise RequestException(f"{error_msg} (HTTP {response.status_code})")
            
            return response.json()
            
        except Timeout:
            raise RequestException(f"Request timeout after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Request failed: {str(e)}")

