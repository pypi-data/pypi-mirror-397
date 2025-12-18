"""Example: List all sessions."""

import os
from noti_sdk_py import configure_client, list_sessions

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        print('📋 Listing all sessions...')
        
        # List all sessions (including STOPPED)
        sessions = list_sessions(query={'all': True})
        
        print(f'✅ Found {len(sessions)} sessions:')
        for session in sessions:
            print(f'  - {session.get("name")}: {session.get("status")}')
            if session.get('me'):
                me = session['me']
                print(f'    User: {me.get("pushName") or me.get("id")}')
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

