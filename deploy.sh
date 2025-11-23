#!/bin/bash

# Configuration
PROJECT_ID="your-project-id"
SERVICE_NAME="benboulanger-ai"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "Building Docker image..."
gcloud builds submit --tag ${IMAGE_NAME}

echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --port 8080 \
  --set-env-vars="OPENAI_API_KEY=${OPENAI_API_KEY}" \
  --project ${PROJECT_ID}

echo "Deployment complete!"
