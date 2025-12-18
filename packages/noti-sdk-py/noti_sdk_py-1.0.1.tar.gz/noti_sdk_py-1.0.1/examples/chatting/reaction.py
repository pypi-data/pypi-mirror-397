"""Example: Add or remove a reaction to a message."""

import os
from noti_sdk_py import configure_client, reaction

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        message_id = 'true_51111111111@c.us_3EB09B7F7C4D979850CD33'  # Change to a real messageId
        
        print('👍 Adding reaction to message...')
        
        result = reaction(
            body={
                'session': session_name,
                'messageId': message_id,
                'reaction': '👍'  # Reaction emoji
            }
        )
        
        print('✅ Reaction added:', result)
        
        # To remove a reaction, send an empty string
        # result2 = reaction(
        #     body={
        #         'session': session_name,
        #         'messageId': message_id,
        #         'reaction': ''  # Empty string removes the reaction
        #     }
        # )
        # print('✅ Reaction removed:', result2)
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

