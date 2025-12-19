"""
Tests for TempMailChecker client
"""

import pytest
from tempmailchecker import TempMailChecker, ENDPOINT_EU, ENDPOINT_US, ENDPOINT_ASIA
from requests.exceptions import RequestException


class TestTempMailChecker:
    """Test TempMailChecker client"""
    
    @pytest.fixture
    def api_key(self):
        """Get API key from environment or use placeholder"""
        import os
        return os.getenv('TEMPMAILCHECKER_API_KEY', 'test_key')
    
    @pytest.fixture
    def checker(self, api_key):
        """Create TempMailChecker instance"""
        if api_key == 'test_key':
            pytest.skip('TEMPMAILCHECKER_API_KEY not set')
        return TempMailChecker(api_key)
    
    def test_initialization(self, api_key):
        """Test client initialization"""
        checker = TempMailChecker(api_key)
        assert checker is not None
        assert checker.api_key == api_key
    
    def test_requires_api_key(self):
        """Test that API key is required"""
        with pytest.raises(ValueError, match="API key is required"):
            TempMailChecker('')
    
    def test_set_timeout(self, api_key):
        """Test setting timeout"""
        checker = TempMailChecker(api_key)
        result = checker.set_timeout(15)
        assert result is checker
        assert checker.timeout == 15
    
    def test_check_valid_email(self, checker):
        """Test checking valid email"""
        result = checker.check('test@gmail.com')
        assert isinstance(result, dict)
        assert 'temp' in result
        assert isinstance(result['temp'], bool)
    
    def test_is_disposable_method(self, checker):
        """Test is_disposable method"""
        result = checker.is_disposable('test@10minutemail.com')
        assert isinstance(result, bool)
    
    def test_check_domain(self, checker):
        """Test checking domain"""
        result = checker.check_domain('tempmail.com')
        assert isinstance(result, dict)
        assert 'temp' in result
    
    def test_invalid_email_format(self, checker):
        """Test invalid email format"""
        with pytest.raises(ValueError, match="Invalid email address format"):
            checker.check('not-an-email')
    
    def test_empty_email(self, checker):
        """Test empty email"""
        with pytest.raises(ValueError, match="Email address is required"):
            checker.check('')
    
    def test_endpoint_constants(self):
        """Test endpoint constants"""
        assert ENDPOINT_EU == 'https://tempmailchecker.com'
        assert ENDPOINT_US == 'https://us.tempmailchecker.com'
        assert ENDPOINT_ASIA == 'https://asia.tempmailchecker.com'
    
    def test_custom_endpoint(self, api_key):
        """Test custom endpoint"""
        checker = TempMailChecker(api_key, endpoint=ENDPOINT_US)
        assert checker.endpoint == ENDPOINT_US
    
    def test_get_usage(self, checker):
        """Test getting usage statistics"""
        usage = checker.get_usage()
        assert isinstance(usage, dict)
        assert 'usage_today' in usage
        assert 'limit' in usage
        assert 'reset' in usage

