"""HTTP request utility for the NotiBuzz SDK."""

import json
import warnings
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin, urlencode

# Suppress urllib3 OpenSSL warnings (common on macOS with LibreSSL)
# This is handled at the package level in __init__.py, but we also add it here
# as a safeguard in case this module is imported directly
warnings.filterwarnings('ignore', message='.*urllib3.*OpenSSL.*')
warnings.filterwarnings('ignore', message='.*LibreSSL.*')
warnings.filterwarnings('ignore', category=UserWarning, module='urllib3')

import requests


class RequestOptions:
    """Options for HTTP requests."""
    
    def __init__(
        self,
        method: str,
        base_url: str,
        path: str,
        api_key: str,
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.method = method
        self.base_url = base_url
        self.path = path
        self.api_key = api_key
        self.query = query or {}
        self.body = body
        self.headers = headers or {}


def request(opts: RequestOptions) -> Any:
    """
    Make an HTTP request to the NotiBuzz API.
    
    Args:
        opts: Request options containing method, URL, API key, etc.
        
    Returns:
        The JSON response parsed as a Python object.
        
    Raises:
        requests.RequestException: If the request fails.
        ValueError: If the API key is missing.
    """
    # Ensure base_url ends with / and path doesn't start with /
    base_url = opts.base_url if opts.base_url.endswith("/") else f"{opts.base_url}/"
    path = opts.path.lstrip("/")
    url = urljoin(base_url, path)
    
    # Build query parameters
    query_params = {}
    for key, value in opts.query.items():
        if value is not None:
            if isinstance(value, (list, tuple)):
                # For arrays, append each item
                for item in value:
                    if item is not None:
                        query_params[key] = item
            else:
                query_params[key] = str(value)
    
    # Ensure API key is present
    if not opts.api_key:
        raise ValueError("API Key is required")
    
    api_key_value = str(opts.api_key).strip()
    
    # Build headers
    headers = {**opts.headers}
    
    # Add Content-Type for POST/PUT requests or when body is present
    if opts.body is not None or opts.method in ("POST", "PUT"):
        headers["Content-Type"] = "application/json"
    
    # Always include X-Api-Key header
    headers["X-Api-Key"] = api_key_value
    
    # Prepare body
    body_data = None
    if opts.method == "GET":
        body_data = None
    elif opts.method == "DELETE":
        # DELETE only sends body if explicitly defined
        body_data = json.dumps(opts.body) if opts.body is not None else None
    else:
        # POST and PUT always send body (can be empty object)
        body_data = json.dumps(opts.body if opts.body is not None else {})
    
    # Debug logging (if DEBUG env var is set)
    import os
    if os.getenv("DEBUG") or os.getenv("NODE_ENV") == "development":
        print("🔍 Request Debug:")
        print(f"  URL: {url}")
        print(f"  Method: {opts.method}")
        print(f"  Headers: {json.dumps(headers, indent=2)}")
        print(f"  Body: {body_data or '(none)'}")
        print(f"  API Key present: {bool(api_key_value)}")
        print(f"  API Key length: {len(api_key_value)}")
    
    # Make the request
    response = requests.request(
        method=opts.method,
        url=url,
        params=query_params if query_params else None,
        headers=headers,
        data=body_data,
    )
    
    # Parse response
    try:
        data = response.json() if response.text else None
    except json.JSONDecodeError:
        data = response.text
    
    # Raise exception for non-2xx status codes
    if not response.ok:
        error_msg = (
            f"HTTP {response.status_code} {response.reason} - "
            f"{data if isinstance(data, str) else json.dumps(data)}"
        )
        raise requests.RequestException(error_msg)
    
    return data

