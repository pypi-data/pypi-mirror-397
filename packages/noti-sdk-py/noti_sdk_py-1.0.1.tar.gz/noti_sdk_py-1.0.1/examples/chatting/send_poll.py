"""Example: Send a poll."""

import os
from noti_sdk_py import configure_client, send_message

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        chat_id = '51111111111@c.us'
        
        print('📊 Sending poll...')
        
        result = send_message(
            body={
                'type': 'poll',
                'payload': {
                    'session': session_name,
                    'chatId': chat_id,
                    'poll': {
                        'name': 'What is your favorite color?',
                        'options': ['Red', 'Blue', 'Green', 'Yellow'],
                        'selectableOptionsCount': 1  # 1 = single selection, >1 = multiple
                    }
                }
            }
        )
        
        print('✅ Poll sent:', result)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

