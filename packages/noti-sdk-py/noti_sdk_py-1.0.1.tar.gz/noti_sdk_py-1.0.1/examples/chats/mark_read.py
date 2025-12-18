"""Example: Mark messages as read."""

import os
from noti_sdk_py import configure_client, chats_read_messages

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        chat_id = '51111111111@c.us'
        
        print('✅ Marking messages as read...')
        
        result = chats_read_messages(
            path_params={
                'session': session_name,
                'chatId': chat_id
            },
            query={
                'messages': 30,  # Number of messages to mark
                'days': 7  # Days back
            }
        )
        
        ids = result.get('ids', [])
        print(f'✅ Messages marked as read: {len(ids)}')
        if ids:
            print('Message IDs:', ids)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

