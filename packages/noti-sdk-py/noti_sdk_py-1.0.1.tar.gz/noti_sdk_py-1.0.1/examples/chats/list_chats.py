"""Example: List chats."""

import os
import json
from noti_sdk_py import configure_client, chats_overview_get

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        
        print('💬 Listing chats...')
        
        chats = chats_overview_get(
            path_params={'session': session_name},
            query={
                'limit': 20,
                'offset': 0
            }
        )
        
        print('Chats:', json.dumps(chats, indent=2))
        
        print(f'✅ Found {len(chats)} chats:')
        for chat in chats:
            print(f'  - {chat.get("name") or chat.get("id")}')
            if chat.get('lastMessage'):
                print(f'    Last message: {chat["lastMessage"].get("body") or "(no text)"}')
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

