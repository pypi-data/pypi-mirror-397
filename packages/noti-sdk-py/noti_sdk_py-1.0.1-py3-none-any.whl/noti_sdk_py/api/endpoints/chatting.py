"""Chatting endpoints for NotiBuzz SDK."""

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union
from urllib.parse import quote

from ..client import get_client, RequestOptions


# Message types supported by sendMessage
MessageType = Literal[
    "text",
    "image",
    "file",
    "voice",
    "video",
    "link-custom-preview",
    "seen",
    "poll",
    "location",
    "contact-vcard",
    "forward",
    "list",
]


def _make_path(template: str, params: Optional[Dict[str, Any]] = None) -> str:
    """Replace path parameters in template with actual values."""
    if not params:
        return template
    result = template
    for key, value in params.items():
        result = result.replace(f"{{{key}}}", quote(str(value)))
    return result


def send_message(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
    async_: Optional[bool] = None,
) -> Any:
    """
    Send messages in batch or individually using the generic /api/sendMessage endpoint.
    This is the only endpoint for sending messages in the bridge.
    
    Supports two modes:
    1. Bulk mode: {'messages': [{'type': ..., 'payload': ...}], 'intervalMs': ...}
    2. Individual mode: {'type': ..., 'payload': ...}
    
    Supported types according to TYPE_PATH_MAP:
    - 'text' → /api/sendText
    - 'image' → /api/sendImage
    - 'file' → /api/sendFile
    - 'voice' → /api/sendVoice
    - 'video' → /api/sendVideo
    - 'link-custom-preview' → /api/send/link-custom-preview
    - 'seen' → /api/sendSeen
    - 'poll' → /api/sendPoll
    - 'location' → /api/sendLocation
    - 'contact-vcard' → /api/sendContactVcard
    - 'forward' → /api/forwardMessage
    - 'list' → /api/sendList
    
    Note: 'typing-start' and 'typing-stop' have direct endpoints (/api/startTyping and /api/stopTyping)
    
    Method: POST
    Path: /api/sendMessage
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters.
        body: Request body with message data.
        async_: Whether to send asynchronously (enqueue).
        
    Returns:
        Message sending result.
    """
    path = _make_path("/api/sendMessage", path_params)
    options = RequestOptions(query=query, async_=async_)
    return get_client().post(path, body, options)


def reaction(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Add or remove a reaction on a message.
    This endpoint does NOT go through sendMessage, it's direct.
    
    Method: PUT
    Path: /api/reaction
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters.
        body: Request body with reaction data.
        
    Returns:
        Reaction result.
    """
    path = _make_path("/api/reaction", path_params)
    return get_client().put(path, body)


def start_typing(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
    async_: Optional[bool] = None,
) -> Any:
    """
    Start typing status in a chat.
    This endpoint does NOT go through sendMessage, it's direct.
    
    Method: POST
    Path: /api/startTyping
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters.
        body: Request body with session and chatId.
        async_: Whether to send asynchronously.
        
    Returns:
        Typing status result.
    """
    path = _make_path("/api/startTyping", path_params)
    options = RequestOptions(query=query, async_=async_)
    return get_client().post(path, body, options)


def stop_typing(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
    async_: Optional[bool] = None,
) -> Any:
    """
    Stop typing status in a chat.
    This endpoint does NOT go through sendMessage, it's direct.
    
    Method: POST
    Path: /api/stopTyping
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters.
        body: Request body with session and chatId.
        async_: Whether to send asynchronously.
        
    Returns:
        Typing status result.
    """
    path = _make_path("/api/stopTyping", path_params)
    options = RequestOptions(query=query, async_=async_)
    return get_client().post(path, body, options)

