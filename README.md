# Zoom Integration

A FastAPI application that integrates with Zoom webhooks to process meeting recordings.

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