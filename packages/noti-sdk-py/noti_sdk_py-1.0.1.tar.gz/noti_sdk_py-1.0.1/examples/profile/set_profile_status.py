"""Example: Update profile status (About)."""

import os
from noti_sdk_py import configure_client, set_profile_status

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        new_status = '🎉 Using Noti Sender!'  # Change to your desired status
        
        print(f'✏️ Updating profile status...')
        
        result = set_profile_status(
            path_params={'session': session_name},
            body={'status': new_status}
        )
        
        print('✅ Profile status updated:', result)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

