"""Example: Send bulk messages."""

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
        
        print('📨 Sending bulk messages...')
        
        result = send_message(
            body={
                'intervalMs': 20000,  # 20 seconds between messages
                'messages': [
                    {
                        'type': 'text',
                        'payload': {
                            'session': session_name,
                            'chatId': '51111111111@c.us',
                            'text': 'Message 1: Hello! 👋'
                        }
                    },
                    {
                        'type': 'text',
                        'payload': {
                            'session': session_name,
                            'chatId': '51111111111@c.us',
                            'text': 'Message 2: How are you?'
                        }
                    },
                    {
                        'type': 'image',
                        'payload': {
                            'session': session_name,
                            'chatId': '51111111111@c.us',
                            'file': {
                                'mimetype': 'image/jpeg',
                                'url': 'https://picsum.photos/400/300'
                            },
                            'caption': 'Message 3: Bulk image (URL)'
                        }
                    }
                ],
                'meta': {
                    'campaignId': 'campaign-123',
                    'requester': 'my-app',
                    'origin': 'sdk-example'
                }
            }
        )
        
        print('✅ Bulk campaign enqueued:')
        print(f'  Job ID: {result.get("jobId")}')
        print(f'  Messages: {result.get("count")}')
        print(f'  Interval: {result.get("intervalMs")}ms')
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

