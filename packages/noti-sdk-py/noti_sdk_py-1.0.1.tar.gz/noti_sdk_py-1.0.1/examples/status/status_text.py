"""Example: Create a text status."""

import os
from noti_sdk_py import configure_client, status_text

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        
        print('📝 Creating text status...')
        
        result = status_text(
            path_params={'session': session_name},
            body={
                'id': None,  # Required: must be None
                'contacts': ['51111111111@c.us', '51111111111@c.us'],  # Duplicates and malformed are automatically filtered
                'text': 'Check out my new status! 🎉',
                'backgroundColor': '#38b42f',
                'font': 0,
                'linkPreview': True,
                'linkPreviewHighQuality': False
            }
        )
        
        print('✅ Text status created:', result)
        
        # To send to specific contacts:
        # result2 = status_text(
        #     path_params={'session': session_name},
        #     body={
        #         'contacts': ['51987654321@c.us', '51987654322@c.us'],
        #         'text': 'Status only for some contacts',
        #         'backgroundColor': '#38b42f',
        #         'font': 0
        #     }
        # )
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

