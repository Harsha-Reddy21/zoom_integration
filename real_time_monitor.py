import os
import requests
import time
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')

def get_access_token():
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"
    response = requests.post(url, auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET))
    return response.json().get('access_token')

def monitor_active_meetings():
    access_token = get_access_token()
    if not access_token:
        print("Failed to get access token")
        return
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get user ID
    user_response = requests.get("https://api.zoom.us/v2/users/me", headers=headers)
    if user_response.status_code != 200:
        print(f"Failed to get user info: {user_response.status_code}")
        return
    
    user_id = user_response.json().get('id')
    
    # Monitor active meetings
    while True:
        try:
            # Get live meetings
            meetings_url = f"https://api.zoom.us/v2/users/{user_id}/meetings"
            meetings_response = requests.get(meetings_url, headers=headers, 
                                           params={"type": "live"})
            
            if meetings_response.status_code == 200:
                meetings = meetings_response.json().get("meetings", [])
                
                for meeting in meetings:
                    meeting_id = meeting.get("id")
                    print(f"Active meeting: {meeting.get('topic')} (ID: {meeting_id})")
                    
                    # Get meeting participants
                    participants_url = f"https://api.zoom.us/v2/metrics/meetings/{meeting_id}/participants"
                    participants_response = requests.get(participants_url, headers=headers)
                    
                    if participants_response.status_code == 200:
                        participants = participants_response.json().get("participants", [])
                        print(f"  Participants: {len(participants)}")
                        
                        # Here you would implement your real-time monitoring logic
                        # For example, saving participant data, checking video status, etc.
            else:
                print(f"Failed to get meetings: {meetings_response.status_code}")
            
            # Check every 60 seconds
            time.sleep(60)
            
        except Exception as e:
            print(f"Error monitoring meetings: {e}")
            time.sleep(60)

if __name__ == "__main__":
    monitor_active_meetings()
