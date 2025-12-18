"""
Official Python SDK for NotiBuzz.

A simple and powerful client for sending WhatsApp messages, managing media,
and interacting with NotiBuzz APIs from any Python application or backend service.
"""

# IMPORTANT: Suppress urllib3 OpenSSL warnings BEFORE any other imports
# This must be done first to prevent the warning from appearing when urllib3
# is imported (which happens when requests is imported)
import warnings
warnings.filterwarnings('ignore', message='.*urllib3.*OpenSSL.*')
warnings.filterwarnings('ignore', message='.*LibreSSL.*')
warnings.filterwarnings('ignore', category=UserWarning, module='urllib3')

from .api.client import configure_client, get_client, NotiSenderClient, ClientConfig
from .api.endpoints import (
    # Sessions
    list_sessions,
    get_session,
    get_session_me,
    # Profile
    get_my_profile,
    set_profile_name,
    set_profile_status,
    set_profile_picture,
    delete_profile_picture,
    # Chatting
    send_message,
    reaction,
    start_typing,
    stop_typing,
    # Status
    status_text,
    status_image,
    status_voice,
    status_video,
    status_delete,
    # Chats
    chats_get,
    chats_overview_get,
    chats_overview_post,
    chats_get_messages,
    chats_read_messages,
    chats_get_message,
    chats_delete_message,
    chats_edit_message,
    chats_pin_message,
    chats_unpin_message,
    # Contacts
    contacts_get_all,
    contacts_get_basic,
    contacts_check_exists,
    contacts_profile_picture,
    contacts_get_about,
    contacts_block,
    contacts_unblock,
    contacts_upsert,
    # Bulk
    bulk_stop_campaign,
    bulk_resume_campaign,
    bulk_availability,
)
from .api.endpoints.chatting import MessageType

__version__ = "1.0.1"
__all__ = [
    # Client
    "configure_client",
    "get_client",
    "NotiSenderClient",
    "ClientConfig",
    # Sessions
    "list_sessions",
    "get_session",
    "get_session_me",
    # Profile
    "get_my_profile",
    "set_profile_name",
    "set_profile_status",
    "set_profile_picture",
    "delete_profile_picture",
    # Chatting
    "send_message",
    "reaction",
    "start_typing",
    "stop_typing",
    "MessageType",
    # Status
    "status_text",
    "status_image",
    "status_voice",
    "status_video",
    "status_delete",
    # Chats
    "chats_get",
    "chats_overview_get",
    "chats_overview_post",
    "chats_get_messages",
    "chats_read_messages",
    "chats_get_message",
    "chats_delete_message",
    "chats_edit_message",
    "chats_pin_message",
    "chats_unpin_message",
    # Contacts
    "contacts_get_all",
    "contacts_get_basic",
    "contacts_check_exists",
    "contacts_profile_picture",
    "contacts_get_about",
    "contacts_block",
    "contacts_unblock",
    "contacts_upsert",
    # Bulk
    "bulk_stop_campaign",
    "bulk_resume_campaign",
    "bulk_availability",
]

