import os
import json
import asyncio
import websockets
import requests
import logging
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Zoom API credentials
ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')

class ZoomRTMSClient:
    def __init__(self):
        self.access_token = None
        self.rtms_token = None
        self.websocket = None
        self.meeting_id = None
        self.rtms_url = "wss://rtms.zoom.us/v1"

    def get_access_token(self):
        """Get OAuth access token from Zoom"""
        url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"
        response = requests.post(url, auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET))
        if response.status_code == 200:
            self.access_token = response.json().get('access_token')
            return self.access_token
        else:
            logger.error(f"Failed to get access token: {response.status_code} - {response.text}")
            return None

    def get_rtms_token(self, meeting_id):
        """Get RTMS token for a specific meeting"""
        if not self.access_token:
            self.get_access_token()
            
        if not self.access_token:
            logger.error("No access token available")
            return None
            
        url = f"https://api.zoom.us/v2/rtms/meetings/{meeting_id}/tokens"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.rtms_token = response.json().get('token')
            self.meeting_id = meeting_id
            return self.rtms_token
        else:
            logger.error(f"Failed to get RTMS token: {response.status_code} - {response.text}")
            return None

    async def connect_to_rtms(self, meeting_id):
        """Connect to RTMS websocket for a meeting"""
        if not self.rtms_token or self.meeting_id != meeting_id:
            self.get_rtms_token(meeting_id)
            
        if not self.rtms_token:
            logger.error("No RTMS token available")
            return False
            
        try:
            # Connect to RTMS WebSocket
            self.websocket = await websockets.connect(
                f"{self.rtms_url}?access_token={self.rtms_token}",
                extra_headers={"Content-Type": "application/json"}
            )
            
            # Subscribe to video streams
            await self.subscribe_to_streams()
            
            logger.info(f"Connected to RTMS for meeting {meeting_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RTMS: {e}")
            return False

    async def subscribe_to_streams(self):
        """Subscribe to specific data streams"""
        if not self.websocket:
            logger.error("WebSocket connection not established")
            return
            
        # Subscribe to video streams
        subscribe_message = {
            "action": "subscribe",
            "streams": [
                {"type": "video", "options": {"quality": "high"}},
                {"type": "audio"},
                {"type": "transcript"}
            ]
        }
        
        await self.websocket.send(json.dumps(subscribe_message))
        logger.info("Subscribed to video, audio, and transcript streams")

    async def process_video_data(self, frame_processor_func=None):
        """Process incoming video frames"""
        if not self.websocket:
            logger.error("WebSocket connection not established")
            return
            
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                # Process different types of data
                if "video" in data:
                    video_data = data["video"]
                    logger.info(f"Received video frame: {len(video_data)} bytes")
                    
                    # Process the video frame if a processor function is provided
                    if frame_processor_func:
                        await frame_processor_func(video_data)
                        
                elif "audio" in data:
                    audio_data = data["audio"]
                    logger.info(f"Received audio data: {len(audio_data)} bytes")
                    
                elif "transcript" in data:
                    transcript = data["transcript"]
                    logger.info(f"Received transcript: {transcript}")
                    
                elif "error" in data:
                    logger.error(f"RTMS error: {data['error']}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("RTMS connection closed")
        except Exception as e:
            logger.error(f"Error processing RTMS data: {e}")

    async def close(self):
        """Close the RTMS connection"""
        if self.websocket:
            await self.websocket.close()
            logger.info("RTMS connection closed")

# Example frame processor function
async def example_frame_processor(frame_data):
    """Example function to process video frames"""
    # Here you would implement your video processing logic
    # For example, saving frames, running computer vision models, etc.
    print(f"Processing video frame: {len(frame_data)} bytes")
    
    # Example: Save frame to file (in a real implementation, you'd decode the video data first)
    # with open(f"frame_{int(time.time())}.raw", "wb") as f:
    #     f.write(frame_data)

async def monitor_meeting(meeting_id):
    """Monitor a specific meeting"""
    client = ZoomRTMSClient()
    
    # Connect to RTMS
    connected = await client.connect_to_rtms(meeting_id)
    if not connected:
        logger.error(f"Failed to connect to RTMS for meeting {meeting_id}")
        return
    
    try:
        # Process video data
        await client.process_video_data(example_frame_processor)
    finally:
        # Close connection when done
        await client.close()

# Main function to run the RTMS client
async def main():
    # Replace with your meeting ID
    meeting_id = "your_meeting_id"
    
    # Monitor the meeting
    await monitor_meeting(meeting_id)

if __name__ == "__main__":
    asyncio.run(main())
