"""Example: Delete a status."""

import os
from noti_sdk_py import configure_client, status_delete

# Configure client
configure_client({
    'noti_url': os.getenv('NOTI_URL', 'your_base_url'),
    'noti_api_key': os.getenv('NOTI_KEY', 'your_api_key')
})

def main():
    try:
        session_name = os.getenv('NOTI_SESSION_NAME', 'default')
        status_id = '3EB0D04B6D96D71FEDC2AD'  # ID of the status to delete
        
        print('🗑️ Deleting status...')
        
        # Note: id must be a valid string (status ID), contacts must have at least one element
        result = status_delete(
            path_params={'session': session_name},
            body={
                'id': status_id,  # Required: ID of the status to delete (string)
                'contacts': ['51111111111@c.us']  # Required: at least one contact (duplicates and malformed are automatically filtered)
            }
        )
        
        print('✅ Status deleted:', result)
        
        # Example with multiple contacts:
        # result2 = status_delete(
        #     path_params={'session': session_name},
        #     body={
        #         'id': status_id,  # ID of the status to delete
        #         'contacts': ['51987654321@c.us', '51987654322@c.us']  # Minimum one contact required
        #     }
        # )
    except Exception as error:
        print('❌ Error:', str(error))

if __name__ == '__main__':
    main()

