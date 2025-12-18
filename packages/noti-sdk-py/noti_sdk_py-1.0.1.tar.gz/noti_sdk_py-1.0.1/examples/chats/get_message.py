"""Example: Get a specific message."""

import os
from datetime import datetime
from noti_sdk_py import configure_client, chats_get_message

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        chat_id = '51111111111@c.us'
        message_id = 'true_51111111111@c.us_3EB02990E1DF2238954274'  # Change to a real messageId
        
        print('📨 Getting specific message...')
        
        message = chats_get_message(
            path_params={
                'session': session_name,
                'chatId': chat_id,
                'messageId': message_id
            },
            query={
                'downloadMedia': True
            }
        )
        
        print('✅ Message obtained:')
        print(f'  ID: {message.get("id")}')
        print(f'  From: {"Me" if message.get("fromMe") else message.get("from")}')
        print(f'  Body: {message.get("body") or "(media)"}')
        timestamp = message.get('timestamp')
        if timestamp:
            print(f'  Timestamp: {datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")}')
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

