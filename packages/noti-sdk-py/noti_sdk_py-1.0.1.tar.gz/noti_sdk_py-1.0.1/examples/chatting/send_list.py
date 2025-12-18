"""Example: Send an interactive list."""

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
        chat_id = '51111111111@c.us'
        
        print('📋 Sending interactive list...')
        
        result = send_message(
            body={
                'type': 'list',
                'payload': {
                    'session': session_name,
                    'chatId': chat_id,
                    'message': {
                        'title': 'Simple Menu',
                        'description': 'Please choose an option',
                        'footer': 'Thank you!',
                        'button': 'Choose',
                        'sections': [
                            {
                                'title': 'Main',
                                'rows': [
                                    {
                                        'title': 'Option 1',
                                        'rowId': 'option1',
                                        'description': 'Option 1 description'
                                    },
                                    {
                                        'title': 'Option 2',
                                        'rowId': 'option2',
                                        'description': 'Option 2 description'
                                    },
                                    {
                                        'title': 'Option 3',
                                        'rowId': 'option3',
                                        'description': 'Option 3 description'
                                    }
                                ]
                            }
                        ]
                    },
                    'reply_to': None
                }
            }
        )
        
        print('✅ List sent:', result)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

