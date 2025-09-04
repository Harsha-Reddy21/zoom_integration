# Zoom Integration

A FastAPI application that integrates with Zoom webhooks to process meeting recordings and real-time video streams.

## Features

- Webhook integration for Zoom events
- Processing of meeting recordings
- Real-time video processing using Zoom RTMS (Realtime Media Streams)
- Face detection and video frame analysis

## Local Development

### Environment Variables

Create a `.env` file with the following variables:

```
ZOOM_ACCOUNT_ID=your_zoom_account_id
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
ZOOM_VERIFICATION_TOKEN=your_zoom_verification_token
```

### Running with Docker

1. Build and run the Docker container:

```bash
docker-compose up
```

The API will be available at http://localhost:8000

## Using the Real-Time Video Processing

1. Configure your Zoom app to use RTMS:
   - In the Zoom Marketplace, go to your app's configuration
   - Enable "Realtime Media Streams" feature
   - Add the necessary scopes: `meeting:read`, `meeting:write`, `rtms:read`, `rtms:write`

2. Start RTMS processing for a meeting:
   - Automatic: When a meeting starts, the webhook will trigger RTMS processing
   - Manual: Call the `/start-rtms/{meeting_id}` endpoint with your meeting ID

3. Processed video frames will be saved in the `video_output` directory

## API Endpoints

- `GET /` - Health check endpoint
- `POST /webhook` - Zoom webhook endpoint
- `GET /meetings` - List Zoom meetings
- `GET /start-rtms/{meeting_id}` - Manually start RTMS for a meeting

## Deployment to Render

1. Push your code to a GitHub repository

2. In the Render dashboard, create a new Web Service

3. Select "Deploy an existing image from a registry" and connect your GitHub repository

4. Render will automatically detect the `render.yaml` configuration

5. Set the required environment variables in the Render dashboard:
   - ZOOM_ACCOUNT_ID
   - ZOOM_CLIENT_ID
   - ZOOM_CLIENT_SECRET
   - ZOOM_VERIFICATION_TOKEN

6. Deploy the service

Your API will be available at your Render URL (e.g., https://zoom-integration.onrender.com).

## RTMS Requirements

To use Zoom's Realtime Media Streams (RTMS):

1. Your Zoom account must have RTMS enabled (may require a paid plan)
2. Your app must have the necessary OAuth scopes
3. The meeting host must allow RTMS for their meetings
4. You need to subscribe to the streams you want to process