"""Example: Create a video status."""

import os
from noti_sdk_py import configure_client, status_video

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        
        print('🎥 Creating video status...')
        
        # Video must be MP4 with H.264 codec
        # Note: id must be None, contacts are automatically filtered (duplicates and malformed are omitted)
        
        # Option 1: From URL
        result = status_video(
            path_params={'session': session_name},
            body={
                'id': None,  # Required: must be None
                'contacts': ['51111111111@c.us'],  # Duplicates are automatically filtered
                'caption': 'Check out this video!',
                'file': {
                    'mimetype': 'video/mp4',
                    'filename': 'status.mp4',
                    'url': 'https://example.com/status.mp4'  # ⚠️ Change to your valid URL
                },
                'convert': True  # True if you need format conversion (e.g., other formats to MP4/H.264)
            }
        )
        
        print('✅ Video status created (URL):', result)
        
        # Option 2: From base64
        # result2 = status_video(
        #     path_params={'session': session_name},
        #     body={
        #         'id': None,  # Required: must be None
        #         'contacts': ['51111111111@c.us'],  # Duplicates and malformed are automatically filtered
        #         'caption': 'Video from base64',
        #         'file': {
        #             'mimetype': 'video/mp4',
        #             'filename': 'status.mp4',
        #             'data': 'AAAAGGZ0eXBt....'  # Base64 of MP4 file
        #         },
        #         'convert': False
        #     }
        # )
        # print('✅ Video status created (base64):', result2)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

