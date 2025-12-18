"""Example: Create an image status."""

import os
from noti_sdk_py import configure_client, status_image

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        
        print('📷 Creating image status...')
        
        # Option 1: From URL
        # Note: id must be None, contacts are automatically filtered (duplicates and malformed are omitted)
        result = status_image(
            path_params={'session': session_name},
            body={
                'id': None,  # Required: must be None
                'contacts': ['51111111111@c.us', '51111111111@c.us'],  # Duplicates are automatically filtered
                'caption': 'My new status with image 📸',
                'file': {
                    'mimetype': 'image/jpeg',
                    'filename': 'status.jpg',
                    'url': 'https://picsum.photos/400/300'
                }
            }
        )
        
        print('✅ Image status created (URL):', result)
        
        # Option 2: From base64
        # result2 = status_image(
        #     path_params={'session': session_name},
        #     body={
        #         'id': None,  # Required: must be None
        #         'contacts': ['51111111111@c.us'],  # Duplicates and malformed are automatically filtered
        #         'caption': 'Status from base64',
        #         'file': {
        #             'mimetype': 'image/jpeg',
        #             'data': '/9j/4AAQSkZJRgABAgAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='  # Base64 example
        #         }
        #     }
        # )
        # print('✅ Image status created (base64):', result2)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

