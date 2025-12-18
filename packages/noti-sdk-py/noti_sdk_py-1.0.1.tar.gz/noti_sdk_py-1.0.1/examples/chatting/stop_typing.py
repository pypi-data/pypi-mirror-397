"""Example: Stop typing status."""

import os
from noti_sdk_py import configure_client, stop_typing

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        chat_id = '51111111111@c.us'
        
        print('⏹️ Stopping typing status...')
        
        result = stop_typing(
            body={
                'session': session_name,
                'chatId': chat_id
            }
        )
        
        print('✅ Typing status stopped:', result)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

