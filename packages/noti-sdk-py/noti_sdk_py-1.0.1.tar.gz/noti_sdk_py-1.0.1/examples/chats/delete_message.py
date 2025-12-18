"""Example: Delete a message."""

import os
from noti_sdk_py import configure_client, chats_delete_message

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        chat_id = '51111111111@c.us'
        message_id = 'true_25718918484128@lid_A5F0519EC89D68E4352A917766747028'
        
        print('🗑️ Deleting message...')
        
        result = chats_delete_message(
            path_params={
                'session': session_name,
                'chatId': chat_id,
                'messageId': message_id
            }
        )
        
        print('✅ Message deleted:', result)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

