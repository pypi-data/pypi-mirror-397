"""Example: Get profile information."""

import os
import json
from noti_sdk_py import configure_client, get_my_profile

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        
        print('👤 Getting profile information...')
        
        profile = get_my_profile(path_params={'session': session_name})
        
        print('✅ Profile:')
        print(json.dumps(profile, indent=2))
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

