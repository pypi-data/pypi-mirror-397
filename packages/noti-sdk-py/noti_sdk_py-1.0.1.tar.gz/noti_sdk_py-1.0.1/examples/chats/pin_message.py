"""Example: Pin or unpin a message."""

import os
from noti_sdk_py import configure_client, chats_pin_message, chats_unpin_message

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        chat_id = '51111111111@c.us'
        message_id = 'false_51111111111@c.us_AAAAAAAAAAAAAAAAAAAA'
        
        print('📌 Pinning message...')
        
        # Pin for 24 hours (86400 seconds)
        result = chats_pin_message(
            path_params={
                'session': session_name,
                'chatId': chat_id,
                'messageId': message_id
            },
            body={
                'duration': 86400  # 24 hours
                # 7 days = 604800
                # 30 days = 2592000
            }
        )
        
        print('✅ Message pinned:', result)
        
        # To unpin:
        # result2 = chats_unpin_message(
        #     path_params={
        #         'session': session_name,
        #         'chatId': chat_id,
        #         'messageId': message_id
        #     }
        # )
        # print('✅ Message unpinned:', result2)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

