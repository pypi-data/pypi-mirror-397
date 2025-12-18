"""Example: Send a message with custom link preview."""

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
        
        print('🔗 Sending message with custom preview...')
        
        result = send_message(
            body={
                'type': 'link-custom-preview',
                'payload': {
                    'session': session_name,
                    'chatId': chat_id,
                    'text': 'Check this out! https://github.com/',
                    'linkPreviewHighQuality': True,
                    'preview': {
                        'image': {
                            'url': 'https://picsum.photos/400/300'
                        },
                        'url': 'https://github.com/',
                        'title': 'Your Title',
                        'description': 'Check this out, amazing!'
                    },
                    'reply_to': None
                }
            }
        )
        
        print('✅ Message with preview sent:', result)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

