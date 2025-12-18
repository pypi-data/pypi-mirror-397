"""Profile endpoints for NotiBuzz SDK."""

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


def get_my_profile(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Get the profile information of the account.
    
    Method: GET
    Path: /api/{session}/profile
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body (not used for GET).
        
    Returns:
        Profile information.
    """
    path = _make_path("/api/{session}/profile", path_params)
    return get_client().get(path, query)


def set_profile_name(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Update the profile name.
    
    Method: PUT
    Path: /api/{session}/profile/name
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body (e.g., {'name': 'New Name'}).
        
    Returns:
        Updated profile information.
    """
    path = _make_path("/api/{session}/profile/name", path_params)
    return get_client().put(path, body)


def set_profile_status(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Update the profile status (About).
    
    Method: PUT
    Path: /api/{session}/profile/status
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body (e.g., {'status': 'New status'}).
        
    Returns:
        Updated profile information.
    """
    path = _make_path("/api/{session}/profile/status", path_params)
    return get_client().put(path, body)


def set_profile_picture(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Update the profile picture; accepts remote file or binary.
    
    Method: PUT
    Path: /api/{session}/profile/picture
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body with file information.
        
    Returns:
        Updated profile information.
    """
    path = _make_path("/api/{session}/profile/picture", path_params)
    return get_client().put(path, body)


def delete_profile_picture(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Delete the profile picture.
    
    Method: DELETE
    Path: /api/{session}/profile/picture
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body (not used for DELETE).
        
    Returns:
        Deletion result.
    """
    path = _make_path("/api/{session}/profile/picture", path_params)
    return get_client().delete(path)

