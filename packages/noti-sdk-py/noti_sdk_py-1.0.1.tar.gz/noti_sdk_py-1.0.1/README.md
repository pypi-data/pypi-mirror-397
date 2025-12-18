# noti-sdk-py

[![PyPI version](https://img.shields.io/pypi/v/noti-sdk-py.svg)](https://pypi.org/project/noti-sdk-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/noti-sdk-py.svg)](https://pypi.org/project/noti-sdk-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**noti-sdk-py** is a lightweight Python SDK for interacting with the Notibuzz Cloud REST API.
It enables Python applications to programmatically send WhatsApp messages, automate notifications, and run bulk messaging campaigns with minimal configuration. Ideal for backend services, automation scripts, and data-driven workflows.

## Features

- ✅ **Full Python support** - Type hints and autocompletion
- ✅ **Bulk messaging** - Support for campaigns with anti-ban control
- ✅ **Async queue** - Background message sending
- ✅ **All endpoints** - Sessions, Profile, Chatting, Status, Chats, Contacts
- ✅ **Campaign control** - Stop, resume and check availability
- ✅ **Pythonic API** - Clean and intuitive interface

## Installation

```bash
pip install noti-sdk-py
```

## Quick Setup

### Option 1: Environment Variables

```bash
export NOTI_URL="your_base_url"
export NOTI_KEY="your_api_key_here"
```

### Option 2: Code Configuration

**Recommended syntax (dict):**
```python
from noti_sdk_py import configure_client

configure_client({
    'noti_url': 'your_base_url',
    'noti_api_key': 'your_api_key'
})
```

**Traditional syntax (also supported):**
```python
configure_client('your_base_url', 'your_api_key')
```

## Basic Usage

### Send a text message

```python
from noti_sdk_py import configure_client, send_message
import os

configure_client({
    'noti_url': os.getenv('NOTI_URL'),
    'noti_api_key': os.getenv('NOTI_KEY')
})

result = send_message(
    body={
        'type': 'text',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
                    'text': 'Hello from the SDK!'
        }
    }
)

print('Message sent:', result)
```

### List sessions

```python
from noti_sdk_py import list_sessions

sessions = list_sessions(
    query={'all': True}  # Include STOPPED sessions
)

print('Available sessions:', sessions)
```

## Bulk Messaging

The SDK supports bulk messaging with interval and anti-ban control:

```python
from noti_sdk_py import send_message

# Bulk sending with multiple messages
result = send_message(
    body={
        'intervalMs': 20000,  # 20 seconds between messages
        'messages': [
            {
                'type': 'text',
                'payload': {
                    'session': 'default',
                    'chatId': '51987654321@c.us',
                    'text': 'Message 1'
                }
            },
            {
                'type': 'text',
                'payload': {
                    'session': 'default',
                    'chatId': '51987654322@c.us',
                    'text': 'Message 2'
                }
            },
            {
                'type': 'image',
                'payload': {
                    'session': 'default',
                    'chatId': '51987654323@c.us',
                    'file': {
                        'mimetype': 'image/jpeg',
                        'filename': 'foto.jpg',
                        'url': 'https://example.com/image.jpg'
                    },
                    'caption': 'Check out this image'
                }
            }
        ],
        'meta': {
            'campaignId': 'campaign-123',
            'requester': 'my-app',
            'origin': 'web'
        }
    }
)

print('Campaign enqueued:', result)
# {'enqueued': True, 'jobId': 'send-bulk-...', 'count': 3, 'intervalMs': 20000}
```

### Individual message using send_message

```python
from noti_sdk_py import send_message

# You can also send an individual message
result = send_message(
    body={
        'type': 'text',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
                    'text': 'Single message'
        }
    }
)
```

## Async Sending

You can send messages asynchronously (queued) using the `async_` parameter:

```python
from noti_sdk_py import send_message

# The message will be queued and processed in the background
send_message(
    body={
        'type': 'text',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'text': 'Async message'
        }
    },
    async_=True  # Queue the message
)

# Also works with other message types
send_message(
    body={
        'type': 'image',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'file': {
                'mimetype': 'image/jpeg',
                'url': 'https://example.com/image.jpg'
            }
        }
    },
    async_=True
)
```

## Bulk Campaign Control

### Check availability

```python
from noti_sdk_py import bulk_availability

availability = bulk_availability(
    query={'requester': 'my-app'}
)

print('Availability:', availability)
# {'available': True, 'current': 1, 'max': 2, 'origin': 'noti-sender-bridge'}
```

### Stop a campaign

```python
from noti_sdk_py import bulk_stop_campaign

bulk_stop_campaign(
    path_params={'id': 'campaign-123'},
    body={
        'sessions': ['default']  # Optional: stop only in these sessions
    }
)
```

### Resume a campaign

```python
from noti_sdk_py import bulk_resume_campaign

bulk_resume_campaign(
    path_params={'id': 'campaign-123'},
    body={
        'sessions': ['default']  # Optional: resume only in these sessions
    }
)
```

## Examples by Category

### Sessions

```python
from noti_sdk_py import list_sessions, get_session, get_session_me

# List all sessions
sessions = list_sessions(query={'all': True})

# Get session information
session = get_session(path_params={'session': 'default'})

# Get authenticated account information
me = get_session_me(path_params={'session': 'default'})
```

### Profile

```python
from noti_sdk_py import (
    get_my_profile,
    set_profile_name,
    set_profile_status,
    set_profile_picture,
    delete_profile_picture
)

# Get profile
profile = get_my_profile(path_params={'session': 'default'})

# Update profile name
set_profile_name(
    path_params={'session': 'default'},
    body={'name': 'My New Name'}
)

# Update status (About)
set_profile_status(
    path_params={'session': 'default'},
    body={'status': '🎉 Using Noti Sender!'}
)

# Update profile picture
set_profile_picture(
    path_params={'session': 'default'},
    body={
        'file': {
            'mimetype': 'image/jpeg',
            'filename': 'avatar.jpg',
            'url': 'https://example.com/avatar.jpg'
        }
    }
)

# Delete profile picture
delete_profile_picture(path_params={'session': 'default'})
```

### Chatting

**Important**: All messages are sent through the generic `send_message` endpoint. Supported types: `text`, `image`, `file`, `voice`, `video`, `link-custom-preview`, `seen`, `poll`, `location`, `contact-vcard`, `forward`, `list`.

**Direct endpoints** (don't go through send_message): `reaction`, `start_typing`, `stop_typing`.

```python
from noti_sdk_py import send_message, reaction, start_typing, stop_typing

# Send text
send_message(
    body={
        'type': 'text',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'text': 'Hello!'
        }
    }
)

# Send image
send_message(
    body={
        'type': 'image',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'file': {
                'mimetype': 'image/jpeg',
                'filename': 'foto.jpg',
                'url': 'https://example.com/image.jpg'
            },
            'caption': 'Check this out'
        }
    }
)

# Send file
send_message(
    body={
        'type': 'file',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'file': {
                'mimetype': 'application/pdf',
                'filename': 'document.pdf',
                'url': 'https://example.com/document.pdf'
            },
            'caption': 'Important document'
        }
    }
)

# Send voice note
send_message(
    body={
        'type': 'voice',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'file': {
                'mimetype': 'audio/ogg; codecs=opus',
                'url': 'https://example.com/voice.opus'
            },
            'convert': False  # True if you need format conversion
        }
    }
)

# Send video
send_message(
    body={
        'type': 'video',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'file': {
                'mimetype': 'video/mp4',
                'filename': 'video.mp4',
                'url': 'https://example.com/video.mp4'
            },
            'caption': 'Watch this video',
            'asNote': False,  # True for round video
            'convert': False
        }
    }
)

# Send poll
send_message(
    body={
        'type': 'poll',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'poll': {
                'name': 'What is your favorite color?',
                'options': ['Red', 'Blue', 'Green'],
                'selectableOptionsCount': 1
            }
        }
    }
)

# Send location
send_message(
    body={
        'type': 'location',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'latitude': -12.097633,
            'longitude': -77.019575,
            'title': 'Our office'
        }
    }
)

# Send contact (vCard)
send_message(
    body={
        'type': 'contact-vcard',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'contacts': [
                {
                    'fullName': 'John Doe',
                    'organization': 'Company Name',
                    'phoneNumber': '+51 987 654 321',
                    'whatsappId': '51987654321'
                }
            ]
        }
    }
)

# Send list (interactive list)
send_message(
    body={
        'type': 'list',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'message': {
                'title': 'Simple Menu',
                'description': 'Please choose an option',
                'footer': 'Thank you!',
                'button': 'Choose',
                'sections': [
                    {
                        'title': 'Main',
                        'rows': [
                            {
                                'title': 'Option 1',
                                'rowId': 'option1',
                                'description': 'Option 1 description'
                            },
                            {
                                'title': 'Option 2',
                                'rowId': 'option2',
                                'description': 'Option 2 description'
                            }
                        ]
                    }
                ]
            }
        }
    }
)

# Send message with custom link preview
send_message(
    body={
        'type': 'link-custom-preview',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'text': 'Check this out! https://github.com/',
            'linkPreviewHighQuality': True,
            'preview': {
                'image': {
                    'url': 'https://picsum.photos/400/300'
                },
                'url': 'https://github.com/',
                'title': 'Your Title',
                'description': 'Check this out, amazing!'
            }
        }
    }
)

# Forward message
send_message(
    body={
        'type': 'forward',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'forward': {
                'keyId': 'true_51987654322@c.us_AAAAAAAAAAAAAAAAAAAA'
            }
        }
    }
)

# Mark as seen using sendMessage with type 'seen'
send_message(
    body={
        'type': 'seen',
        'payload': {
            'session': 'default',
            'chatId': '51987654321@c.us',
            'messages': ['false_51987654321@c.us_AAAAAAAAAAAAAAAAAAAA']
        }
    }
)

# React to a message (direct endpoint)
reaction(
    body={
        'session': 'default',
        'messageId': 'true_51987654321@c.us_3EB0EB3DF63D6AF1112A85',
        'reaction': '👍'
    }
)

# Start typing (direct endpoint)
start_typing(
    body={
        'session': 'default',
        'chatId': '51987654321@c.us'
    }
)

# Stop typing (direct endpoint)
stop_typing(
    body={
        'session': 'default',
        'chatId': '51987654321@c.us'
    }
)
```

### Status (Stories)

```python
from noti_sdk_py import status_text, status_image, status_voice, status_video, status_delete

# Create text Story
status_text(
    path_params={'session': 'default'},
    body={
        'contacts': [],  # [] to send to all
        'text': 'Check this out! https://github.com/',
        'backgroundColor': '#38b42f',
        'font': 0,
        'linkPreview': True
    }
)

# Create image Story
status_image(
    path_params={'session': 'default'},
    body={
        'contacts': ['51987654321@c.us'],
        'caption': 'My Story',
        'file': {
            'mimetype': 'image/jpeg',
            'filename': 'status.jpg',
            'url': 'https://example.com/image.jpg'
        }
    }
)

# Create voice Story
status_voice(
    path_params={'session': 'default'},
    body={
        'contacts': ['51987654321@c.us'],
        'backgroundColor': '#38b42f',
        'file': {
            'mimetype': 'audio/ogg; codecs=opus',
            'url': 'https://example.com/voice.opus'
        },
        'convert': False
    }
)

# Create video Story
status_video(
    path_params={'session': 'default'},
    body={
        'contacts': ['51987654321@c.us'],
        'caption': 'My video Story',
        'file': {
            'mimetype': 'video/mp4',
            'filename': 'status.mp4',
            'url': 'https://example.com/status.mp4'
        },
        'convert': False
    }
)

# Delete Story
status_delete(
    path_params={'session': 'default'},
    body={
        'id': '3EB0B4B74FB349EEC971A6'
    }
)
```

### Chats

```python
from noti_sdk_py import (
    chats_get,
    chats_overview_get,
    chats_overview_post,
    chats_get_messages,
    chats_get_message,
    chats_read_messages,
    chats_delete_message,
    chats_edit_message,
    chats_pin_message,
    chats_unpin_message,
)

# List chats
chats = chats_get(path_params={'session': 'default'})

# Get chat overview
overview = chats_overview_get(
    path_params={'session': 'default'},
    query={'limit': 20, 'offset': 0}
)

# Get chat overview (POST method with filters)
overview_post = chats_overview_post(
    path_params={'session': 'default'},
    body={
        'limit': 20,
        'offset': 0,
        'ids': ['51987654321@c.us']  # Optional: filter by chat IDs
    }
)

# Get chat messages
messages = chats_get_messages(
    path_params={
        'session': 'default',
        'chatId': '51987654321@c.us'
    },
    query={
        'limit': 50,
        'offset': 0,
        'downloadMedia': True
    }
)

# Get a specific message by ID
message = chats_get_message(
    path_params={
        'session': 'default',
        'chatId': '51987654321@c.us',
        'messageId': 'false_51987654321@c.us_AAAAAAAAAAAAAAAAAAAA'
    },
    query={'downloadMedia': True}
)

# Mark messages as read
chats_read_messages(
    path_params={
        'session': 'default',
        'chatId': '51987654321@c.us'
    },
    query={
        'messages': 30,  # Number of messages
        'days': 7  # Days back
    }
)

# Edit message
chats_edit_message(
    path_params={
        'session': 'default',
        'chatId': '51987654321@c.us',
        'messageId': 'false_51987654321@c.us_AAAAAAAAAAAAAAAAAAAA'
    },
    body={
        'text': 'Edited message',
        'linkPreview': True
    }
)

# Delete message
chats_delete_message(
    path_params={
        'session': 'default',
        'chatId': '51987654321@c.us',
        'messageId': 'false_51987654321@c.us_AAAAAAAAAAAAAAAAAAAA'
    }
)

# Pin message
chats_pin_message(
    path_params={
        'session': 'default',
        'chatId': '51987654321@c.us',
        'messageId': 'false_51987654321@c.us_AAAAAAAAAAAAAAAAAAAA'
    },
    body={
        'duration': 86400  # 24 hours
    }
)

# Unpin message
chats_unpin_message(
    path_params={
        'session': 'default',
        'chatId': '51987654321@c.us',
        'messageId': 'false_51987654321@c.us_AAAAAAAAAAAAAAAAAAAA'
    }
)
```

### Contacts

```python
from noti_sdk_py import (
    contacts_get_all,
    contacts_get_basic,
    contacts_check_exists,
    contacts_profile_picture,
    contacts_get_about,
    contacts_block,
    contacts_unblock,
    contacts_upsert,
)

# List all contacts
all_contacts = contacts_get_all(query={'session': 'default'})

# Get basic information
contact = contacts_get_basic(
    query={
        'session': 'default',
        'contactId': '51987654321@c.us'
    }
)

# Check if a number exists in WhatsApp
exists = contacts_check_exists(
    query={
        'session': 'default',
        'phone': '51987654321'
    }
)

# Get profile picture
picture = contacts_profile_picture(
    query={
        'session': 'default',
        'contactId': '51987654321@c.us',
        'refresh': False
    }
)

# Get contact about (status)
about = contacts_get_about(
    query={
        'session': 'default',
        'contactId': '51987654321@c.us'
    }
)

# Block contact
contacts_block(
    path_params={
        'session': 'default',
        'chatId': '51987654321@c.us'
    }
)

# Unblock contact
contacts_unblock(
    path_params={
        'session': 'default',
        'chatId': '51987654321@c.us'
    }
)

# Create or update contact
contacts_upsert(
    path_params={
        'session': 'default',
        'chatId': '51987654321@c.us'
    },
    body={
        'firstName': 'John',
        'lastName': 'Doe'
    }
)
```

## Error Handling

```python
from noti_sdk_py import send_message
import requests

try:
    result = send_message(
        body={
            'type': 'text',
            'payload': {
                'session': 'default',
                'chatId': '51987654321@c.us',
                'text': 'Hello'
            }
        }
    )
    print('Success:', result)
except requests.RequestException as error:
    print('Error:', str(error))
    # Error message includes HTTP code and details
    # Example: "HTTP 401 Unauthorized - { 'error': 'invalid X-Api-Key' }"
```

## Requirements

- Python >= 3.8
- requests >= 2.28.0

## More Examples

For complete, runnable examples organized by category, see the [`examples/`](examples/) directory:

- **Sessions**: List, get session info, get authenticated account
- **Profile**: Get profile, update name/status/picture, delete picture
- **Chatting**: All message types (text, image, file, voice, video, poll, location, contact, list, link preview, forward), reactions, typing indicators
- **Status**: Text, image, voice, video statuses, delete status
- **Chats**: List chats, get messages, edit/delete/pin/unpin messages, mark as read
- **Contacts**: Get contacts, check existence, profile pictures, block/unblock, upsert

Run any example:
```bash
python examples/sessions/list_sessions.py
python examples/chatting/send_text.py
```

## API Reference

All endpoints are documented with type hints. For the complete list of endpoints and their parameters, see the [Bridge documentation](https://github.com/notibuzz/noti-sender-bridge).

### Main Endpoints

- **Sessions**: `list_sessions`, `get_session`, `get_session_me`
- **Profile**: `get_my_profile`, `set_profile_name`, `set_profile_status`, `set_profile_picture`, `delete_profile_picture`
- **Chatting**: `send_message` (generic endpoint for all types: text, image, file, voice, video, poll, location, contact-vcard, forward, list), `reaction`, `start_typing`, `stop_typing`
- **Status**: `status_text`, `status_image`, `status_voice`, `status_video`, `status_delete`
- **Chats**: `chats_get`, `chats_overview_get`, `chats_overview_post`, `chats_get_messages`, `chats_read_messages`, `chats_get_message`, `chats_delete_message`, `chats_edit_message`, `chats_pin_message`, `chats_unpin_message`
- **Contacts**: `contacts_get_all`, `contacts_get_basic`, `contacts_check_exists`, `contacts_profile_picture`, `contacts_get_about`, `contacts_block`, `contacts_unblock`, `contacts_upsert`
- **Bulk**: `bulk_stop_campaign`, `bulk_resume_campaign`, `bulk_availability`

## Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for more details.

## Support

- **Issues**: [GitHub Issues](https://github.com/notibuzzcloud/noti-sdk-py/issues)
- **Documentation**: [README](README.md)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

