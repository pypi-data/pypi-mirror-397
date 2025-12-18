"""Example: Send a file."""

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
        
        print('📄 Sending file...')
        
        # Option 1: From URL
        result = send_message(
            body={
                'type': 'file',
                'payload': {
                    'session': session_name,
                    'chatId': chat_id,
                    'file': {
                        'mimetype': 'application/pdf',
                        'filename': 'document.pdf',
                        'url': 'https://scrumguides.org/docs/scrumguide/v1/Scrum-Guide-ES.pdf'
                    },
                    'caption': 'My CV',
                    'reply_to': None
                }
            }
        )
        
        print('✅ File sent (URL):', result)
        
        # Option 2: From base64
        # result2 = send_message(
        #     body={
        #         'type': 'file',
        #         'payload': {
        #             'session': session_name,
        #             'chatId': chat_id,
        #             'file': {
        #                 'mimetype': 'application/pdf',
        #                 'filename': 'document.pdf',
        #                 'data': '/9j/4AAQSkZJRgABAgAAAQABAAD.......'
        #             },
        #             'caption': 'File from base64'
        #         }
        #     }
        # )
        # print('✅ File sent (base64):', result2)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

