"""Chats endpoints for NotiBuzz SDK."""

from typing import Any, Dict, Optional
from urllib.parse import quote

from ..client import get_client, RequestOptions


def _make_path(template: str, params: Optional[Dict[str, Any]] = None) -> str:
    """Replace path parameters in template with actual values."""
    if not params:
        return template
    result = template
    for key, value in params.items():
        result = result.replace(f"{{{key}}}", quote(str(value)))
    return result


def chats_overview_get(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Get chat overview (id, name, photo, last message). Sorted by last message timestamp.
    
    Method: GET
    Path: /api/{session}/chats/overview
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body (not used for GET).
        
    Returns:
        Chat overview.
    """
    path = _make_path("/api/{session}/chats/overview", path_params)
    return get_client().get(path, query)


def chats_overview_post(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Get chat overview using POST (allows more complex filters).
    
    Method: POST
    Path: /api/{session}/chats/overview
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body with filters.
        
    Returns:
        Chat overview.
    """
    path = _make_path("/api/{session}/chats/overview", path_params)
    return get_client().post(path, body)


def chats_get(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    List chats of the session.
    
    Method: GET
    Path: /api/{session}/chats
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body (not used for GET).
        
    Returns:
        List of chats.
    """
    path = _make_path("/api/{session}/chats", path_params)
    return get_client().get(path, query)


def chats_get_messages(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    List chat messages with filters and pagination. Supports media download.
    
    Method: GET
    Path: /api/{session}/chats/{chatId}/messages
    
    Args:
        path_params: Path parameters (must include 'session' and 'chatId').
        query: Query parameters.
        body: Request body (not used for GET).
        
    Returns:
        List of messages.
    """
    path = _make_path("/api/{session}/chats/{chatId}/messages", path_params)
    return get_client().get(path, query)


def chats_read_messages(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, int]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Mark messages as read (latest first). You can limit by quantity or days.
    Note: The bridge uses query params (messages, days) instead of body.
    
    Method: POST
    Path: /api/{session}/chats/{chatId}/messages/read
    
    Args:
        path_params: Path parameters (must include 'session' and 'chatId').
        query: Query parameters (e.g., {'messages': 30, 'days': 7}).
        body: Request body (not used).
        
    Returns:
        Read result.
    """
    path = _make_path("/api/{session}/chats/{chatId}/messages/read", path_params)
    options = RequestOptions(query=query)
    return get_client().post(path, body, options)


def chats_get_message(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Get a specific message by its ID. Can download associated media.
    
    Method: GET
    Path: /api/{session}/chats/{chatId}/messages/{messageId}
    
    Args:
        path_params: Path parameters (must include 'session', 'chatId', and 'messageId').
        query: Query parameters.
        body: Request body (not used for GET).
        
    Returns:
        Message information.
    """
    path = _make_path("/api/{session}/chats/{chatId}/messages/{messageId}", path_params)
    return get_client().get(path, query)


def chats_delete_message(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Delete a specific message from the chat by its ID.
    
    Method: DELETE
    Path: /api/{session}/chats/{chatId}/messages/{messageId}
    
    Args:
        path_params: Path parameters (must include 'session', 'chatId', and 'messageId').
        query: Query parameters.
        body: Request body (not used for DELETE).
        
    Returns:
        Deletion result.
    """
    path = _make_path("/api/{session}/chats/{chatId}/messages/{messageId}", path_params)
    return get_client().delete(path)


def chats_edit_message(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Edit the content of an existing message. You can include link preview.
    
    Method: PUT
    Path: /api/{session}/chats/{chatId}/messages/{messageId}
    
    Args:
        path_params: Path parameters (must include 'session', 'chatId', and 'messageId').
        query: Query parameters.
        body: Request body with new message content.
        
    Returns:
        Edited message.
    """
    path = _make_path("/api/{session}/chats/{chatId}/messages/{messageId}", path_params)
    return get_client().put(path, body)


def chats_pin_message(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Pin a message within the chat for a specific duration.
    - 24 hours - duration=86400
    - 7 days - duration=604800
    - 30 days - duration=2592000
    
    Method: POST
    Path: /api/{session}/chats/{chatId}/messages/{messageId}/pin
    
    Args:
        path_params: Path parameters (must include 'session', 'chatId', and 'messageId').
        query: Query parameters.
        body: Request body (e.g., {'duration': 86400}).
        
    Returns:
        Pin result.
    """
    path = _make_path("/api/{session}/chats/{chatId}/messages/{messageId}/pin", path_params)
    return get_client().post(path, body)


def chats_unpin_message(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Remove the pin from a message within the chat.
    
    Method: POST
    Path: /api/{session}/chats/{chatId}/messages/{messageId}/unpin
    
    Args:
        path_params: Path parameters (must include 'session', 'chatId', and 'messageId').
        query: Query parameters.
        body: Request body (not used).
        
    Returns:
        Unpin result.
    """
    path = _make_path("/api/{session}/chats/{chatId}/messages/{messageId}/unpin", path_params)
    return get_client().post(path, body)

