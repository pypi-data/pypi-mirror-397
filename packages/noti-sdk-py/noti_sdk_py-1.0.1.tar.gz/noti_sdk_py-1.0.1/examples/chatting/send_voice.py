"""Example: Send a voice note."""

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
        
        print('🎤 Sending voice note...')
        
        # Option 1: From URL
        result = send_message(
            body={
                'type': 'voice',
                'payload': {
                    'session': session_name,
                    'chatId': chat_id,
                    'file': {
                        'mimetype': 'audio/ogg; codecs=opus',
                        'url': 'https://your-voice-file.opus'
                    },
                    'convert': False
                }
            }
        )
        
        print('✅ Voice note sent (URL):', result)
        
        # Option 2: From base64
        # result2 = send_message(
        #     body={
        #         'type': 'voice',
        #         'payload': {
        #             'session': session_name,
        #             'chatId': chat_id,
        #             'file': {
        #                 'mimetype': 'audio/ogg; codecs=opus',
        #                 'filename': 'voice-message.opus',
        #                 'data': 'T2dnUwACAAAAAAAAAAAAX3UXAAAAAJiLB2IBE09w....'
        #             },
        #             'convert': False
        #         }
        #     }
        # )
        # print('✅ Voice note sent (base64):', result2)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

