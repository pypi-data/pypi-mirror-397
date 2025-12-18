"""Example: Get authenticated account information."""

import os
from noti_sdk_py import configure_client, get_session_me

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        
        print(f'👤 Getting authenticated account information for "{session_name}"...')
        
        me = get_session_me(path_params={'session': session_name})
        
        print('✅ Account information:')
        print(f'  ID: {me.get("id")}')
        print(f'  Name: {me.get("pushName", "N/A")}')
        if me.get('lid'):
            print(f'  LID: {me.get("lid")}')
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

