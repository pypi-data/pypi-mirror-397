"""Example: Create a voice status."""

import os
from noti_sdk_py import configure_client, status_voice

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        
        print('🎤 Creating voice status...')
        
        # File must be in OGG (OPUS) format
        # Note: id must be None, contacts are automatically filtered (duplicates and malformed are omitted)
        
        # Option 1: From URL
        result = status_voice(
            path_params={'session': session_name},
            body={
                'id': None,  # Required: must be None
                'contacts': ['51111111111@c.us'],  # Duplicates are automatically filtered
                'backgroundColor': '#38b42f',
                'file': {
                    'mimetype': 'audio/ogg; codecs=opus',
                    'url': 'https://your-voice-file.opus'  # Valid example URL
                },
                'convert': True  # True if you need format conversion (e.g., MP3 to OGG)
            }
        )
        
        print('✅ Voice status created (URL):', result)
        
        # Option 2: From base64
        # result2 = status_voice(
        #     path_params={'session': session_name},
        #     body={
        #         'id': None,  # Required: must be None
        #         'contacts': ['51111111111@c.us'],  # Duplicates and malformed are automatically filtered
        #         'backgroundColor': '#38b42f',
        #         'file': {
        #             'mimetype': 'audio/ogg; codecs=opus',
        #             'data': 'SUQzBAAAAAAAW....'  # Base64 of OGG/OPUS file
        #         },
        #         'convert': False
        #     }
        # )
        # print('✅ Voice status created (base64):', result2)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

