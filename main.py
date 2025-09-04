import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

load_dotenv()

ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')

def get_access_token():

    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"
    
    try:
        response = requests.post(url, auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET))
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": "request_failed", "reason": str(e)}

if __name__ == "__main__":
    
    token = get_access_token()
    print("Access Token:", token)
