"""Sessions endpoints for NotiBuzz SDK."""

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


def list_sessions(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    List all sessions; use ?all=true to include STOPPED.
    
    Method: GET
    Path: /api/sessions
    
    Args:
        path_params: Path parameters (not used for this endpoint).
        query: Query parameters (e.g., {'all': True}).
        body: Request body (not used for GET).
        
    Returns:
        List of sessions.
    """
    path = _make_path("/api/sessions", path_params)
    return get_client().get(path, query)


def get_session(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Get detailed information about a session by name.
    
    Method: GET
    Path: /api/sessions/{session}
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body (not used for GET).
        
    Returns:
        Session information.
    """
    path = _make_path("/api/sessions/{session}", path_params)
    return get_client().get(path, query)


def get_session_me(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Get information about the authenticated account of the session.
    
    Method: GET
    Path: /api/sessions/{session}/me
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body (not used for GET).
        
    Returns:
        Account information.
    """
    path = _make_path("/api/sessions/{session}/me", path_params)
    return get_client().get(path, query)

