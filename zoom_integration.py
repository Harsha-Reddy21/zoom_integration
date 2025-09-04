import os
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import uvicorn
from requests.auth import HTTPBasicAuth
import hashlib
import hmac
import asyncio
from rtms_client import ZoomRTMSClient
from video_processor import VideoProcessor

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

@app.get("/")
async def health_check():
    """Health check endpoint for Render and Zoom webhook validation"""
    return {"status": "ok"}

@app.post("/webhook")
async def zoom_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    event_type = body.get("event")
    
    # Handle Zoom's URL validation
    if event_type == "endpoint.url_validation":
        plain_token = body.get("payload", {}).get("plainToken")
        if plain_token and VERIFICATION_TOKEN:
            # Generate hash for validation
            encoded_token = plain_token.encode('utf-8')
            encoded_secret = VERIFICATION_TOKEN.encode('utf-8')
            hash_object = hmac.new(encoded_secret, encoded_token, hashlib.sha256)
            encrypted_token = hash_object.hexdigest()
            
            return {
                "plainToken": plain_token,
                "encryptedToken": encrypted_token
            }
    
    # Handle regular Zoom events
    if event_type == "meeting.started":
        meeting_id = body.get("payload", {}).get("object", {}).get("id")
        if meeting_id:
            access_token = get_access_token()
            # Start both recording processing and real-time video processing
            background_tasks.add_task(process_recording, meeting_id, access_token)
            background_tasks.add_task(start_rtms_processing, meeting_id)
        return {"status": "processing"}
    
    elif event_type == "recording.completed":
        recording_files = body.get("payload", {}).get("object", {}).get("recording_files", [])
        meeting_id = body.get("payload", {}).get("object", {}).get("id")
        
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

# Function to start RTMS processing
async def start_rtms_processing(meeting_id):
    """Start processing real-time media streams for a meeting"""
    try:
        # Initialize video processor
        processor = VideoProcessor()
        
        # Initialize RTMS client
        client = ZoomRTMSClient()
        
        # Connect to RTMS
        connected = await client.connect_to_rtms(meeting_id)
        if not connected:
            print(f"Failed to connect to RTMS for meeting {meeting_id}")
            return
        
        # Process video data
        await client.process_video_data(processor.process_frame)
    except Exception as e:
        print(f"Error in RTMS processing: {e}")

@app.get("/start-rtms/{meeting_id}")
async def start_rtms(meeting_id: str, background_tasks: BackgroundTasks):
    """Endpoint to manually start RTMS processing for a meeting"""
    background_tasks.add_task(start_rtms_processing, meeting_id)
    return {"status": "RTMS processing started", "meeting_id": meeting_id}

if __name__ == "__main__":
    uvicorn.run("zoom_integration:app", host="0.0.0.0", port=8000, reload=True)