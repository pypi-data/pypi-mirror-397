"""Client configuration and HTTP client for NotiBuzz SDK."""

import os
from typing import Any, Dict, Optional, Union

from ..utils.request import RequestOptions as _RequestOptions, request


class RequestOptions:
    """Options for HTTP requests."""
    
    def __init__(
        self,
        query: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        async_: Optional[bool] = None,
    ):
        self.query = query or {}
        self.headers = headers or {}
        self.async_ = async_


class ClientConfig:
    """Configuration for the NotiSender client."""
    
    def __init__(self, noti_url: str, noti_api_key: str):
        self.noti_url = noti_url
        self.noti_api_key = noti_api_key


class NotiSenderClient:
    """Client for making requests to the NotiBuzz API."""
    
    def __init__(self, base_url: str, api_key: str):
        if not base_url:
            raise ValueError("Base URL is required")
        if not api_key:
            raise ValueError("API Key is required")
        self.base_url = base_url
        self.api_key = api_key
    
    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        """Make a GET request."""
        query = {**(params or {}), **(options.query if options else {})}
        if options and options.async_:
            query["async"] = "true"
        
        headers = {}
        if options:
            if options.async_:
                headers["X-Async"] = "true"
            headers.update(options.headers or {})
        
        return request(
            _RequestOptions(
                method="GET",
                base_url=self.base_url,
                path=path,
                api_key=self.api_key,
                query=query,
                headers=headers,
            )
        )
    
    def post(
        self,
        path: str,
        body: Optional[Any] = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        """Make a POST request."""
        query = options.query if options else {}
        if options and options.async_:
            query["async"] = "true"
        
        headers = {}
        if options:
            if options.async_:
                headers["X-Async"] = "true"
            headers.update(options.headers or {})
        
        return request(
            _RequestOptions(
                method="POST",
                base_url=self.base_url,
                path=path,
                api_key=self.api_key,
                query=query,
                body=body,
                headers=headers,
            )
        )
    
    def put(
        self,
        path: str,
        body: Optional[Any] = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        """Make a PUT request."""
        query = options.query if options else {}
        if options and options.async_:
            query["async"] = "true"
        
        headers = {}
        if options:
            if options.async_:
                headers["X-Async"] = "true"
            headers.update(options.headers or {})
        
        return request(
            _RequestOptions(
                method="PUT",
                base_url=self.base_url,
                path=path,
                api_key=self.api_key,
                query=query,
                body=body,
                headers=headers,
            )
        )
    
    def delete(
        self,
        path: str,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        """Make a DELETE request."""
        query = options.query if options else {}
        if options and options.async_:
            query["async"] = "true"
        
        headers = {}
        if options:
            if options.async_:
                headers["X-Async"] = "true"
            headers.update(options.headers or {})
        
        return request(
            _RequestOptions(
                method="DELETE",
                base_url=self.base_url,
                path=path,
                api_key=self.api_key,
                query=query,
                headers=headers,
            )
        )


_client: Optional[NotiSenderClient] = None


def configure_client(
    config: Union[ClientConfig, str, Dict[str, str]], noti_api_key: Optional[str] = None
) -> None:
    """
    Configure the global client with the base URL and API key.
    
    You can use object syntax:
    ```python
    configure_client({
        'noti_url': 'your_base_url',
        'noti_api_key': 'your_api_key'
    })
    ```
    
    Or traditional syntax (maintained for compatibility):
    ```python
    configure_client('your_base_url', 'your_api_key')
    ```
    
    Args:
        config: Either a ClientConfig object, a dict with 'noti_url' and 'noti_api_key',
                or a string URL (if using traditional syntax).
        noti_api_key: API key (required when using traditional string syntax).
    """
    global _client
    
    if isinstance(config, str):
        # Traditional syntax: configure_client(url, key)
        if not noti_api_key:
            raise ValueError("API Key is required when using string syntax")
        _client = NotiSenderClient(config, noti_api_key)
    elif isinstance(config, dict):
        # Dict syntax: configure_client({'noti_url': ..., 'noti_api_key': ...})
        _client = NotiSenderClient(config["noti_url"], config["noti_api_key"])
    elif isinstance(config, ClientConfig):
        # ClientConfig object syntax
        _client = NotiSenderClient(config.noti_url, config.noti_api_key)
    else:
        raise ValueError("Invalid configuration format")


def get_client() -> NotiSenderClient:
    """
    Get the configured client.
    
    Returns:
        The configured NotiSenderClient instance.
        
    Raises:
        ValueError: If the client is not configured.
    """
    global _client
    
    if _client:
        return _client
    
    # Try to get from environment variables
    env_url = os.getenv("NOTI_URL")
    env_key = os.getenv("NOTI_KEY")
    
    if env_url and env_key:
        _client = NotiSenderClient(env_url, env_key)
        return _client
    
    raise ValueError(
        "NotiSenderClient not configured. Call configure_client({'noti_url': ..., 'noti_api_key': ...}) "
        "or configure_client(url, key) or set NOTI_URL/NOTI_KEY environment variables."
    )

