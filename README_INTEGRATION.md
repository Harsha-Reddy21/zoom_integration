# Real-Time Zoom Integration

This integration allows for real-time monitoring of Zoom meetings without relying on manual recording uploads.

## Setup

1. Create a Server-to-Server OAuth app in Zoom Marketplace
2. Configure the app with these scopes:
   - meeting:read:admin
   - recording:read:admin
   - user:read:admin

3. Set up webhook events in your Zoom app:
   - meeting.started
   - meeting.ended
   - recording.completed

4. Update your `.env` file with the credentials:
   ```
   ZOOM_ACCOUNT_ID=your_account_id
   ZOOM_CLIENT_ID=your_client_id
   ZOOM_CLIENT_SECRET=your_client_secret
   ZOOM_VERIFICATION_TOKEN=your_webhook_verification_token
   ```

## Running the Integration

### FastAPI Server (Webhook Receiver)
```
python zoom_integration.py
```

### Real-Time Monitor
```
python real_time_monitor.py
```

## Features

- **Real-Time Monitoring**: Monitors active Zoom meetings
- **Webhook Integration**: Receives events when meetings start/end
- **Recording Access**: Automatically processes recordings when completed
- **100% Transparency**: No manual uploads needed, all sessions are tracked
