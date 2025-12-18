"""Example: Create or update a contact."""

import os
from noti_sdk_py import configure_client, contacts_upsert

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        chat_id = '51111111111@c.us'
        
        print('📝 Creating/updating contact...')
        
        result = contacts_upsert(
            path_params={
                'session': session_name,
                'chatId': chat_id
            },
            body={
                'firstName': 'John',
                'lastName': 'Doe'
            }
        )
        
        print('✅ Contact created/updated:', result)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

