"""Example: Update profile picture."""

import os
from noti_sdk_py import configure_client, set_profile_picture

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        
        print('🖼️ Updating profile picture...')
        
        # Option 1: From URL
        result = set_profile_picture(
            path_params={'session': session_name},
            body={
                'file': {
                    'mimetype': 'image/jpeg',
                    'filename': 'avatar.jpg',
                    'url': 'https://example.com/avatar.jpg'
                }
            }
        )
        
        print('✅ Profile picture updated (URL):', result)
        
        # Option 2: From base64
        # result2 = set_profile_picture(
        #     path_params={'session': session_name},
        #     body={
        #         'file': {
        #             'mimetype': 'image/jpeg',
        #             'filename': 'avatar.jpg',
        #             'data': '/9j/4AAQSkZJRgABAgAAAQABAAD...'
        #         }
        #     }
        # )
        # print('✅ Profile picture updated (base64):', result2)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

