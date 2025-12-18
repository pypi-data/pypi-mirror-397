"""Status endpoints for NotiBuzz SDK."""

from typing import Any, Dict, List, Optional
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


def _validate_and_normalize_contacts(contacts: Any) -> List[str]:
    """Validate and normalize contacts array."""
    if contacts is None:
        raise ValueError("contacts is required and must be an array with at least one element")
    if not isinstance(contacts, (list, tuple)):
        raise ValueError("contacts must be an array")
    if len(contacts) == 0:
        raise ValueError("contacts must have at least one element")
    
    normalized = []
    for i, contact in enumerate(contacts):
        if not isinstance(contact, str) or not contact.strip():
            raise ValueError(f"contacts[{i}] must be a non-empty string")
        trimmed = contact.strip()
        
        # Validate format: must be digits only or digits@c.us, no @g.us or @lid
        if "@g.us" in trimmed:
            raise ValueError(f"contacts[{i}] cannot contain @g.us (group chats not allowed)")
        if "@lid" in trimmed:
            raise ValueError(f"contacts[{i}] cannot contain @lid (LID format not allowed)")
        
        # Normalize: if it's just digits, keep as is; if it has @c.us, keep as is
        if "@c.us" in trimmed:
            # Validate it's a valid @c.us format
            import re
            if not re.match(r"^(\d+)@c\.us$", trimmed):
                raise ValueError(f"contacts[{i}] has invalid format. Expected format: digits or digits@c.us")
            normalized.append(trimmed)
        else:
            # Just digits, validate it's only digits
            import re
            if not re.match(r"^\d+$", trimmed):
                raise ValueError(f"contacts[{i}] must contain only digits or be in format digits@c.us")
            normalized.append(trimmed)
    
    return normalized


def _process_status_request(endpoint: str, body: Any) -> Any:
    """Process status request with batching support."""
    is_delete_endpoint = "/status/delete" in endpoint
    
    # For delete endpoint, id must be a valid string
    # For other status endpoints, id must be null
    if is_delete_endpoint:
        if not body.get("id") or not isinstance(body.get("id"), str) or not body.get("id").strip():
            raise ValueError("id is required and must be a non-empty string for delete endpoint")
    else:
        # For create endpoints (text, image, voice, video), id must be null
        if body.get("id") is not None:
            raise ValueError("id must be null for status creation endpoints")
    
    # Validate and normalize contacts
    normalized_contacts = _validate_and_normalize_contacts(body.get("contacts"))
    
    # Build request body: for delete, keep id as is; for create, ensure id is null
    base_body = {k: v for k, v in body.items() if k != "contacts"}
    if is_delete_endpoint:
        base_body["contacts"] = normalized_contacts  # Keep id for delete
    else:
        base_body["id"] = None
        base_body["contacts"] = normalized_contacts  # Set id to null for create
    
    # If contacts <= 10, process directly
    if len(normalized_contacts) <= 10:
        request_body = {**base_body, "contacts": normalized_contacts}
        return get_client().post(endpoint, request_body)
    
    # Process in batches of 10
    batch_size = 10
    batches = [
        normalized_contacts[i : i + batch_size]
        for i in range(0, len(normalized_contacts), batch_size)
    ]
    
    results = []
    errors = []
    
    for i, batch in enumerate(batches):
        request_body = {**base_body, "contacts": batch}
        try:
            result = get_client().post(endpoint, request_body)
            results.append({"batch": i + 1, "totalBatches": len(batches), "result": result})
        except Exception as e:
            errors.append({"batch": i + 1, "totalBatches": len(batches), "error": str(e)})
    
    return {
        "batched": True,
        "totalContacts": len(normalized_contacts),
        "totalBatches": len(batches),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors if errors else None,
    }


def status_text(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Publish a text status; can include link preview.
    
    Method: POST
    Path: /api/{session}/status/text
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body with status data.
        
    Returns:
        Status creation result.
    """
    path = _make_path("/api/{session}/status/text", path_params)
    return _process_status_request(path, body or {})


def status_image(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Publish an image status (URL or Base64).
    
    Method: POST
    Path: /api/{session}/status/image
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body with image data.
        
    Returns:
        Status creation result.
    """
    path = _make_path("/api/{session}/status/image", path_params)
    return _process_status_request(path, body or {})


def status_voice(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Publish a voice status (OGG/OPUS).
    
    Method: POST
    Path: /api/{session}/status/voice
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body with voice data.
        
    Returns:
        Status creation result.
    """
    path = _make_path("/api/{session}/status/voice", path_params)
    return _process_status_request(path, body or {})


def status_video(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Publish a video status (MP4/H.264).
    
    Method: POST
    Path: /api/{session}/status/video
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body with video data.
        
    Returns:
        Status creation result.
    """
    path = _make_path("/api/{session}/status/video", path_params)
    return _process_status_request(path, body or {})


def status_delete(
    path_params: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
) -> Any:
    """
    Delete a status.
    
    Method: POST
    Path: /api/{session}/status/delete
    
    Args:
        path_params: Path parameters (must include 'session').
        query: Query parameters.
        body: Request body with status id and contacts.
        
    Returns:
        Status deletion result.
    """
    path = _make_path("/api/{session}/status/delete", path_params)
    return _process_status_request(path, body or {})

