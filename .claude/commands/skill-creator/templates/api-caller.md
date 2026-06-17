---
name: api-caller
description: Call external APIs with authentication and error handling. Use when integrating with external services, making API requests, or when user mentions API, API integration, or external service.
allowed-tools: Read, Write, Edit, Bash
---

# API Caller

Integrates with external APIs, handling authentication, rate limiting, and error responses.

## When This Skill Activates

- User asks to "call an API", "integrate with [service]", "make API request"
- User mentions "API integration", "external service", "REST API", "GraphQL"
- User needs to connect to a third-party service

## API Integration Workflow

### Step 1: Understand the API

Ask the user for:

1. **API Documentation URL**: Where is the API documented?
2. **Authentication Method**: API key, OAuth, bearer token, basic auth?
3. **Base URL**: What's the API base URL?
4. **Required Operations**: What endpoints do you need to call?

### Step 2: Set Up Authentication

Create a secure authentication setup:

```python
# For API Key authentication
import os

API_KEY = os.getenv("SERVICE_API_KEY")
if not API_KEY:
    raise ValueError("SERVICE_API_KEY environment variable not set")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
```

For OAuth, implement the token flow:

```python
# For OAuth2
import requests

def get_access_token():
    response = requests.post(
        "https://auth.example.com/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": os.getenv("OAUTH_CLIENT_ID"),
            "client_secret": os.getenv("OAUTH_CLIENT_SECRET"),
        }
    )
    return response.json()["access_token"]
```

### Step 3: Create API Client

Generate a clean API client class:

```python
import requests
from typing import Any, Dict

class ServiceAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.example.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an API request with error handling."""
        url = f"{self.base_url}/{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """Get a specific resource."""
        return self._request("GET", f"resources/{resource_id}")

    def create_resource(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource."""
        return self._request("POST", "resources", json=data)
```

### Step 4: Implement Rate Limiting

Add rate limit protection:

```python
import time
from functools import wraps

def rate_limit(calls_per_second: float):
    """Rate limit decorator."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage:
@rate_limit(calls_per_second=10)
def api_call():
    # Your API call here
    pass
```

### Step 5: Handle Errors

Implement comprehensive error handling:

```python
class APIError(Exception):
    """Base API error."""
    pass

class RateLimitError(APIError):
    """Rate limit exceeded."""
    pass

class AuthenticationError(APIError):
    """Authentication failed."""
    pass

def handle_api_response(response: requests.Response):
    """Handle API response with proper error handling."""
    if response.status_code == 401:
        raise AuthenticationError("Invalid API credentials")
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        raise RateLimitError(f"Rate limited. Retry after {retry_after}s")
    if response.status_code >= 400:
        raise APIError(f"API error: {response.status_code} - {response.text}")
    return response.json()
```

### Step 6: Write Tests

Create test examples:

```python
# Example usage
api = ServiceAPI(api_key=os.getenv("SERVICE_API_KEY"))

# Get a resource
resource = api.get_resource("123")

# Create a resource
new_resource = api.create_resource({"name": "Example"})
```

## Environment Setup

Create a `.env.example` file:

```
SERVICE_API_KEY=your_api_key_here
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
```

## Examples

See [examples.md](examples.md) for complete integration examples.

## Troubleshooting

### Authentication Failures
- Verify API key is correct and active
- Check if the key has required permissions
- Ensure headers match API documentation

### Rate Limiting
- Implement exponential backoff
- Cache responses when possible
- Consider batch operations

### Response Format Changes
- Validate response schema
- Handle missing fields gracefully
- Log unexpected formats for debugging
