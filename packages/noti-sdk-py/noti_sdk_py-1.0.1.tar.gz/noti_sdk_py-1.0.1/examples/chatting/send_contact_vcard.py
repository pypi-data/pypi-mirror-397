"""Example: Send a contact (vCard)."""

import os
from noti_sdk_py import configure_client, send_message

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        chat_id = '51111111111@c.us'  # Chat where the contact will be sent
        
        print('👤 Sending contact (vCard)...')
        
        result = send_message(
            body={
                'type': 'contact-vcard',
                'payload': {
                    'session': session_name,
                    'chatId': chat_id,
                    'contacts': [
                        {
                            'fullName': 'John Doe',
                            'organization': 'Company Name',
                            'phoneNumber': '+1 234 567 8900',
                            'whatsappId': '12345678900'
                        }
                    ],
                    'reply_to': None
                }
            }
        )
        
        print('✅ Contact sent:', result)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

