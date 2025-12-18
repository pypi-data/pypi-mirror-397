"""Example: Send a video."""

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
        
        print('🎥 Sending video...')
        
        # Option 1: From URL
        result = send_message(
            body={
                'type': 'video',
                'payload': {
                    'session': session_name,
                    'chatId': chat_id,
                    'file': {
                        'mimetype': 'video/mp4',
                        'filename': 'video.mp4',
                        'url': 'https://example.com/video.mp4'
                    },
                    'caption': 'Watch this video!',
                    'asNote': False,
                    'convert': False
                }
            }
        )
        
        print('✅ Video sent (URL):', result)
        
        # Option 2: From base64
        # result2 = send_message(
        #     body={
        #         'type': 'video',
        #         'payload': {
        #             'session': session_name,
        #             'chatId': chat_id,
        #             'file': {
        #                 'mimetype': 'video/mp4',
        #                 'filename': 'video.mp4',
        #                 'data': 'AAAAGGZ0eXBtcDQyAAAAAGlzb21tc....'
        #             },
        #             'caption': 'Video from base64',
        #             'asNote': False,
        #             'convert': False
        #         }
        #     }
        # )
        # print('✅ Video sent (base64):', result2)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

