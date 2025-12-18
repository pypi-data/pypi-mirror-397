"""Example: Get contact information."""

import os
from noti_sdk_py import configure_client, contacts_get_basic

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        contact_id = '51111111111@c.us'
        
        print(f'👤 Getting contact information for {contact_id}...')
        
        contact = contacts_get_basic(
            query={
                'session': session_name,
                'contactId': contact_id
            }
        )
        
        print('✅ Contact information:')
        print(f'  ID: {contact.get("id")}')
        print(f'  Name: {contact.get("name") or "No name"}')
        if contact.get('pushname'):
            print(f'  Push Name: {contact.get("pushname")}')
        if contact.get('lid'):
            print(f'  LID: {contact.get("lid")}')
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

