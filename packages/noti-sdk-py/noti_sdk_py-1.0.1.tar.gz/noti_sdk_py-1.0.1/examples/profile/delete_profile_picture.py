"""Example: Delete profile picture."""

import os
from noti_sdk_py import configure_client, delete_profile_picture

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        
        print('🗑️ Deleting profile picture...')
        
        result = delete_profile_picture(path_params={'session': session_name})
        
        print('✅ Profile picture deleted:', result)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

