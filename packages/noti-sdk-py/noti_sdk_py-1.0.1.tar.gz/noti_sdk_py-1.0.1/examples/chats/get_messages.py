"""Example: Get chat messages."""

import os
from noti_sdk_py import configure_client, chats_get_messages

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        chat_id = '51111111111@c.us'
        
        print(f'📨 Getting messages from chat {chat_id}...')
        
        messages = chats_get_messages(
            path_params={
                'session': session_name,
                'chatId': chat_id
            },
            query={
                'limit': 200,
                'offset': 0,
                'downloadMedia': True
            }
        )
        
        print(f'✅ Found {len(messages)} messages:')
        for msg in messages:
            # print(f'  ID: {msg.get("id")}')
            from_me = msg.get('fromMe', False)
            from_user = msg.get('from', 'Unknown')
            body = msg.get('body') or '(media)'
            print(f'  [{"Me" if from_me else from_user}]: {body}')
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

