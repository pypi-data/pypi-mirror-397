"""Contacts endpoints for NotiBuzz SDK."""

from typing import Any, Dict, Optional
from urllib.parse import quote

from ..client import get_client


def _make_path(template: str, params: Optional[Dict[str, Any]] = None) -> str:
    """Replace path parameters in template with actual values."""
    if not params:
        return template
    result = template
    for key, value in params.items():
        result = result.replace(f"{{{key}}}", quote(str(value)))
    return result


def contacts_get_basic(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Get basic contact data. Use /contacts/check-exists to verify if the number is registered.
    
    Method: GET
    Path: /api/contacts
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters (e.g., {'session': 'default', 'contactId': '...'}).
        body: Request body (not used for GET).
        
    Returns:
        Basic contact information.
    """
    path = _make_path("/api/contacts", path_params)
    return get_client().get(path, query)


def contacts_get_all(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Get all contacts.
    
    Method: GET
    Path: /api/contacts/all
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters (e.g., {'session': 'default'}).
        body: Request body (not used for GET).
        
    Returns:
        List of all contacts.
    """
    path = _make_path("/api/contacts/all", path_params)
    return get_client().get(path, query)


def contacts_check_exists(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Check if the number is registered in WhatsApp.
    
    Method: GET
    Path: /api/contacts/check-exists
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters (e.g., {'session': 'default', 'phone': '51987654321'}).
        body: Request body (not used for GET).
        
    Returns:
        Existence check result.
    """
    path = _make_path("/api/contacts/check-exists", path_params)
    return get_client().get(path, query)


def contacts_profile_picture(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Get the profile picture URL. May return null for privacy. Use refresh to force update.
    
    Method: GET
    Path: /api/contacts/profile-picture
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters (e.g., {'session': 'default', 'contactId': '...', 'refresh': True}).
        body: Request body (not used for GET).
        
    Returns:
        Profile picture URL.
    """
    path = _make_path("/api/contacts/profile-picture", path_params)
    return get_client().get(path, query)


def contacts_get_about(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Get the contact's "About" (status).
    
    Method: GET
    Path: /api/contacts/about
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters (e.g., {'session': 'default', 'contactId': '...'}).
        body: Request body (not used for GET).
        
    Returns:
        Contact's about/status.
    """
    path = _make_path("/api/contacts/about", path_params)
    return get_client().get(path, query)


def contacts_block(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Block a contact.
    
    Method: POST
    Path: /api/contacts/block
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters.
        body: Request body (e.g., {'session': 'default', 'contactId': '...'}).
        
    Returns:
        Block result.
    """
    path = _make_path("/api/contacts/block", path_params)
    return get_client().post(path, body)


def contacts_unblock(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Unblock a contact.
    
    Method: POST
    Path: /api/contacts/unblock
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters.
        body: Request body (e.g., {'session': 'default', 'contactId': '...'}).
        
    Returns:
        Unblock result.
    """
    path = _make_path("/api/contacts/unblock", path_params)
    return get_client().post(path, body)


def contacts_upsert(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Create or update the contact in the device's address book.
    
    Method: PUT
    Path: /api/{session}/contacts/{chatId}
    
    Args:
        path_params: Path parameters (must include 'session' and 'chatId').
        query: Query parameters.
        body: Request body (e.g., {'firstName': 'John', 'lastName': 'Doe'}).
        
    Returns:
        Upsert result.
    """
    path = _make_path("/api/{session}/contacts/{chatId}", path_params)
    return get_client().put(path, body)

