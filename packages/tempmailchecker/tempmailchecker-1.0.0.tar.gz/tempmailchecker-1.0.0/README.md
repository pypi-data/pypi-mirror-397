<div align="center">
  <img src="header.png" alt="TempMailChecker Python SDK" width="100%">
</div>

# TempMailChecker Python SDK

[![Latest Release](https://img.shields.io/pypi/v/tempmailchecker?style=flat-square&logo=pypi)](https://pypi.org/project/tempmailchecker/)
[![License](https://img.shields.io/pypi/l/tempmailchecker?style=flat-square)](LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/tempmailchecker?style=flat-square&logo=python)](https://python.org)
[![GitHub stars](https://img.shields.io/github/stars/Fushey/python-disposable-email-checker?style=flat-square)](https://github.com/Fushey/python-disposable-email-checker/stargazers)

> **Detect disposable email addresses in real-time** with the TempMailChecker API. Block fake signups, prevent spam, and protect your platform from abuse.

## 🚀 Quick Start

### Installation

```bash
pip install tempmailchecker
# or
pip3 install tempmailchecker
```

### Basic Usage

```python
from tempmailchecker import TempMailChecker

# Initialize with your API key
checker = TempMailChecker('your_api_key_here')

# Check if an email is disposable
if checker.is_disposable('user@tempmail.com'):
    print('Blocked: This is a disposable email')
else:
    print('Valid: This is a legitimate email')
```

## 📖 Documentation

### Check Email Address

```python
checker = TempMailChecker('your_api_key')

# Simple boolean check
is_disposable = checker.is_disposable('test@10minutemail.com')

# Get full response
result = checker.check('user@example.com')
# Returns: {'temp': False}
```

### Check Domain

```python
# Check just the domain
is_disposable = checker.is_disposable_domain('tempmail.com')

# Get full response
result = checker.check_domain('guerrillamail.com')
```

### Regional Endpoints

Use regional endpoints for lower latency. All endpoints use `/check` and `/usage` directly (no `/api` prefix):

```python
from tempmailchecker import TempMailChecker, ENDPOINT_EU, ENDPOINT_US, ENDPOINT_ASIA

# EU endpoint (default)
checker = TempMailChecker('your_api_key')
# or explicitly:
checker = TempMailChecker('your_api_key', endpoint=ENDPOINT_EU)

# US endpoint
checker = TempMailChecker('your_api_key', endpoint=ENDPOINT_US)

# Asia endpoint
checker = TempMailChecker('your_api_key', endpoint=ENDPOINT_ASIA)
```

### Check Usage

```python
usage = checker.get_usage()
# Returns: {'usage_today': 15, 'limit': 25, 'reset': 'midnight UTC'}
```

### Error Handling

```python
from tempmailchecker import TempMailChecker
from requests.exceptions import RequestException

try:
    is_disposable = checker.is_disposable('user@example.com')
except RequestException as e:
    if 'Rate limit' in str(e):
        # Handle rate limit
        pass
    else:
        # Handle other errors
        print(f'Error: {e}')
```

## 🎯 Use Cases

- **Block Fake Signups**: Stop disposable emails at registration
- **Prevent Promo Abuse**: Protect referral programs and coupons
- **Clean Email Lists**: Remove throwaway addresses from newsletters
- **Reduce Spam**: Filter out disposable emails in contact forms
- **Protect Communities**: Ensure real users in forums and chat

## ⚡ Features

- ✅ **Simple API**: One method call, one boolean response
- ✅ **Fast**: Sub-millisecond processing, ~70ms real-world latency
- ✅ **Massive Database**: 277,000+ disposable email domains
- ✅ **Auto-Updates**: Database updated daily automatically
- ✅ **Regional Endpoints**: US, EU, and Asia for optimal performance
- ✅ **Type Hints**: Full type annotations included
- ✅ **Free Tier**: 25 requests/day, no credit card required

## 🔑 Get Your API Key

1. Sign up at [tempmailchecker.com](https://tempmailchecker.com/signup)
2. Get 25 free requests per day
3. Start blocking disposable emails immediately

## 📚 Examples

### Django Integration

```python
from django.core.exceptions import ValidationError
from tempmailchecker import TempMailChecker

def validate_email_not_disposable(email):
    checker = TempMailChecker(settings.TEMPMAILCHECKER_API_KEY)
    
    try:
        if checker.is_disposable(email):
            raise ValidationError('Disposable email addresses are not allowed')
    except RequestException:
        # Fail open - allow email on API error
        pass
```

### Flask Integration

```python
from flask import Flask, request, jsonify
from tempmailchecker import TempMailChecker

app = Flask(__name__)
checker = TempMailChecker(os.getenv('TEMPMAILCHECKER_API_KEY'))

@app.route('/signup', methods=['POST'])
def signup():
    email = request.json.get('email')
    
    try:
        if checker.is_disposable(email):
            return jsonify({'error': 'Disposable email not allowed'}), 400
    except RequestException as e:
        # Log error but allow signup
        app.logger.warning(f'TempMailChecker error: {e}')
    
    # Proceed with signup
    return jsonify({'success': True})
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import EmailStr
from tempmailchecker import TempMailChecker

app = FastAPI()
checker = TempMailChecker(os.getenv('TEMPMAILCHECKER_API_KEY'))

@app.post('/signup')
async def signup(email: EmailStr):
    try:
        if checker.is_disposable(email):
            raise HTTPException(status_code=400, detail='Disposable email not allowed')
    except RequestException:
        # Fail open
        pass
    
    return {'success': True}
```

## 🛠️ Requirements

- Python 3.7 or higher
- requests library (installed automatically)

## 📝 License

This library is open-source software licensed under the [MIT License](LICENSE).

## 🤝 Support

- **Documentation**: [tempmailchecker.com/docs](https://tempmailchecker.com/docs)
- **Issues**: [GitHub Issues](https://github.com/Fushey/python-disposable-email-checker/issues)
- **Email**: support@tempmailchecker.com

## ⭐ Why TempMailChecker?

- **277,000+ domains** in our database
- **Sub-millisecond** API processing
- **~70ms latency** from global endpoints
- **Auto-updates** daily
- **Free tier** with 25 requests/day
- **Simple Python API** - no complex dependencies

---

Made with ❤️ by [TempMailChecker](https://tempmailchecker.com)

