import os
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import uvicorn
from requests.auth import HTTPBasicAuth

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')
VERIFICATION_TOKEN = os.getenv('ZOOM_VERIFICATION_TOKEN')

class ZoomEvent(BaseModel):
    event: str
    payload: dict

def get_access_token():
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"
    response = requests.post(url, auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET))
    return response.json().get('access_token')

async def process_recording(meeting_id: str, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get recording info
    recording_url = f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings"
    response = requests.get(recording_url, headers=headers)
    
    if response.status_code == 200:
        recording_data = response.json()
        # Process recording data here
        # Save to database, analyze, etc.
        return recording_data
    return None

@app.post("/webhook")
async def zoom_webhook(event: ZoomEvent, background_tasks: BackgroundTasks):
    if event.event == "meeting.started":
        meeting_id = event.payload.get("object", {}).get("id")
        if meeting_id:
            access_token = get_access_token()
            background_tasks.add_task(process_recording, meeting_id, access_token)
        return {"status": "processing"}
    
    elif event.event == "recording.completed":
        recording_files = event.payload.get("object", {}).get("recording_files", [])
        meeting_id = event.payload.get("object", {}).get("id")
        
        if recording_files and meeting_id:
            access_token = get_access_token()
            background_tasks.add_task(process_recording, meeting_id, access_token)
        return {"status": "processing"}
    
    return {"status": "ignored"}

@app.get("/meetings")
async def list_meetings():
    access_token = get_access_token()
    print("access_token")
    print(access_token)
    if not access_token:
        raise HTTPException(status_code=401, detail="Failed to get access token")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.zoom.us/v2/users/me/meetings", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to get meetings")

if __name__ == "__main__":
    uvicorn.run("zoom_integration:app", host="0.0.0.0", port=8000, reload=True)
    # print("Hello")
    # print(get_access_token())
