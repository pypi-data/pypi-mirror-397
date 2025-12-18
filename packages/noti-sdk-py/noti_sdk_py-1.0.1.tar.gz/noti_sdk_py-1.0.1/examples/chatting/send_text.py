"""Example: Send a text message."""

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
        chat_id = '51111111111@c.us'  # Change to your real chatId
        
        print('💬 Sending text message...')
        
        result = send_message(
            body={
                'type': 'text',
                'payload': {
                    'session': session_name,
                    'chatId': chat_id,
                    'text': 'Hello from noti-sdk-py! 👋'
                }
            }
        )
        
        print('✅ Message sent:', result)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

