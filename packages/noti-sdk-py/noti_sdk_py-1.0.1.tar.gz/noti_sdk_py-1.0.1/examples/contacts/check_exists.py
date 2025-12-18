"""Example: Check if a number exists on WhatsApp."""

import os
from noti_sdk_py import configure_client, contacts_check_exists

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        phone = '51111111111'  # Number without + or suffix
        
        print(f'🔍 Checking if number {phone} exists on WhatsApp...')
        
        result = contacts_check_exists(
            query={
                'session': session_name,
                'phone': phone
            }
        )
        
        if result.get('numberExists'):
            print(f'✅ Number {phone} is registered on WhatsApp')
            print(f'   Chat ID: {result.get("chatId")}')
        else:
            print(f'❌ Number {phone} is NOT registered on WhatsApp')
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

