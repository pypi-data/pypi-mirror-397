"""Example: Update profile name."""

import os
from noti_sdk_py import configure_client, set_profile_name

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        new_name = 'My New Name'  # Change to your desired name
        
        print(f'✏️ Updating profile name to "{new_name}"...')
        
        result = set_profile_name(
            path_params={'session': session_name},
            body={'name': new_name}
        )
        
        print('✅ Profile name updated:', result)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

