"""Example: Get contact profile picture."""

import os
from noti_sdk_py import configure_client, contacts_profile_picture

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        contact_id = '51111111111@c.us'
        
        print('📷 Getting contact profile picture...')
        
        result = contacts_profile_picture(
            query={
                'session': session_name,
                'contactId': contact_id,
                'refresh': False  # True to force update
            }
        )
        
        if result.get('profilePictureURL'):
            print('✅ Profile picture found:')
            print(f'   URL: {result.get("profilePictureURL")}')
        else:
            print('ℹ️ Contact does not have a profile picture or it is private')
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

