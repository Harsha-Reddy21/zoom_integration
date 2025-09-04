import requests
from main import get_access_token

def list_meetings(access_token):
    """
    List upcoming meetings using Zoom API
    
    Args:
        access_token (str): The OAuth access token
        
    Returns:
        dict: The JSON response containing meeting data
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get the user's ID (you can also specify a user ID directly)
    user_response = requests.get('https://api.zoom.us/v2/users/me', headers=headers)
    if user_response.status_code != 200:
        return {"error": "Failed to get user info", "status_code": user_response.status_code}
    
    user_id = user_response.json().get('id')
    
    # List the user's meetings
    meetings_url = f'https://api.zoom.us/v2/users/{user_id}/meetings'
    meetings_response = requests.get(meetings_url, headers=headers)
    
    if meetings_response.status_code == 200:
        return meetings_response.json()
    else:
        return {"error": "Failed to get meetings", "status_code": meetings_response.status_code}

if __name__ == "__main__":
    # Get access token
    token_response = get_access_token()
    
    if 'access_token' in token_response:
        access_token = token_response['access_token']
        print(f"Access token obtained successfully: {access_token[:10]}...")
        
        # Use the token to list meetings
        meetings = list_meetings(access_token)
        print("\nMeetings:")
        print(meetings)
    else:
        print(f"Failed to get access token: {token_response}")
