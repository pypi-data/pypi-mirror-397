"""Example: Send an image."""

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
        
        print('🖼️ Sending image...')
        
        # Option 1: From URL
        result = send_message(
            body={
                'type': 'image',
                'payload': {
                    'session': session_name,
                    'chatId': chat_id,
                    'file': {
                        'mimetype': 'image/jpeg',
                        'filename': 'photo.jpg',
                        'url': 'https://picsum.photos/400/300',
                    },
                    'caption': 'Check out this image from the SDK! 📸'
                }
            }
        )
        
        print('✅ Image sent (URL):', result)
        
        # Option 2: From base64
        # result2 = send_message(
        #     body={
        #         'type': 'image',
        #         'payload': {
        #             'session': session_name,
        #             'chatId': chat_id,
        #             'file': {
        #                 'mimetype': 'image/jpeg',
        #                 'filename': 'photo.jpg',
        #                 'data': '/9j/4AAQSkZJRgABAgAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='
        #             },
        #             'caption': 'Image from base64'
        #         }
        #     }
        # )
        # print('✅ Image sent (base64):', result2)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

