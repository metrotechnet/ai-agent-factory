# Configuration
$PROJECT_ID = "your-project-id"
$SERVICE_NAME = "benboulanger-ai"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host "Building Docker image..." -ForegroundColor Green
gcloud builds submit --tag $IMAGE_NAME

Write-Host "Deploying to Cloud Run..." -ForegroundColor Cyan
gcloud run deploy $SERVICE_NAME `
  --image $IMAGE_NAME `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --memory 1Gi `
  --cpu 1 `
  --timeout 300 `
  --max-instances 10 `
  --port 8080 `
  --set-env-vars="OPENAI_API_KEY=$env:OPENAI_API_KEY" `
  --project $PROJECT_ID

Write-Host "Deployment complete!" -ForegroundColor Green
