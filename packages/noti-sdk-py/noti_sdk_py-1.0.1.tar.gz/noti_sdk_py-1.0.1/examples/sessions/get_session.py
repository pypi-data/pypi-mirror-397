"""Example: Get session information."""

import os
from noti_sdk_py import configure_client, get_session

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        
        print(f'📋 Getting session information for "{session_name}"...')
        
        session = get_session(path_params={'session': session_name})
        
        print('✅ Session information:')
        print(f'  Name: {session.get("name")}')
        print(f'  Status: {session.get("status")}')
        if session.get('me'):
            me = session['me']
            print(f'  User: {me.get("pushName") or me.get("id")}')
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

