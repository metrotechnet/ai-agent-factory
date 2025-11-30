# Ben Nutritionist AI Deployment Script
# This script builds and deploys the Ben Nutritionist AI assistant to Google Cloud Run

param(
    [string]$Tag = "latest",
    [string]$ProjectId = "bennutritioniste-ai",
    [string]$Region = "us-east4",
    [string]$ServiceName = "ben-nutritionist",
    [switch]$SkipBuild = $false,
    [switch]$Help = $false
)

# Show help
if ($Help) {
    Write-Host "Ben Nutritionist AI Deployment Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Tag <string>        Docker image tag (default: latest)"
    Write-Host "  -ProjectId <string>  Google Cloud project ID (default: bennutritioniste-ai)"
    Write-Host "  -Region <string>     Google Cloud region (default: us-east4)"
    Write-Host "  -ServiceName <string> Cloud Run service name (default: ben-nutritionist)"
    Write-Host "  -SkipBuild          Skip building the Docker image"
    Write-Host "  -Help               Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy.ps1                    # Build and deploy with defaults"
    Write-Host "  .\deploy.ps1 -Tag v1.2.3        # Deploy with specific tag"
    Write-Host "  .\deploy.ps1 -SkipBuild         # Only update Cloud Run service"
    exit 0
}

# Configuration
$ImageName = "$Region-docker.pkg.dev/$ProjectId/$ProjectId-docker-repo/ben-nutritionist"
$FullImageName = "${ImageName}:${Tag}"

Write-Host "=== Ben Nutritionist AI Deployment ===" -ForegroundColor Green
Write-Host "Project ID: $ProjectId"
Write-Host "Region: $Region  "
Write-Host "Service: $ServiceName"
Write-Host "Image: $FullImageName"
Write-Host "Skip Build: $SkipBuild"
Write-Host ""

# Function to check if command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Load environment variables from .env file
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    Write-Host "✅ Environment variables loaded from .env" -ForegroundColor Green
} else {
    Write-Host "⚠️ No .env file found - make sure OPENAI_API_KEY is set" -ForegroundColor Yellow
}

if (!(Test-Command "gcloud")) {
    Write-Host "❌ Google Cloud CLI (gcloud) not found. Please install it first." -ForegroundColor Red
    exit 1
}

if (!(Test-Command "docker") -and !$SkipBuild) {
    Write-Host "❌ Docker not found. Please install Docker Desktop or use -SkipBuild flag." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Check authentication
Write-Host "Checking Google Cloud authentication..." -ForegroundColor Yellow
$AuthCheck = gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>$null
if (!$AuthCheck) {
    Write-Host "❌ Not authenticated with Google Cloud. Please run: gcloud auth login" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Authenticated as: $AuthCheck" -ForegroundColor Green

# Set project
Write-Host "Setting project to $ProjectId..." -ForegroundColor Yellow
gcloud config set project $ProjectId
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set project" -ForegroundColor Red
    exit 1
}

# Build and push Docker image
if (!$SkipBuild) {
    Write-Host "Building and pushing Docker image..." -ForegroundColor Yellow
    
    # Use Cloud Build for building
    Write-Host "Using Google Cloud Build to build image..." -ForegroundColor Cyan
    gcloud builds submit --tag $FullImageName .
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to build and push image" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Image built and pushed successfully" -ForegroundColor Green
} else {
    Write-Host "⏭️ Skipping build step" -ForegroundColor Yellow
}

# Check if service exists
Write-Host "Checking if Cloud Run service exists..." -ForegroundColor Yellow
$ServiceExists = gcloud run services describe $ServiceName --region=$Region --format="value(metadata.name)" 2>$null

if ($ServiceExists) {
    Write-Host "Updating existing Cloud Run service..." -ForegroundColor Yellow
    
    # Update the service
    gcloud run deploy $ServiceName `
        --image $FullImageName `
        --region $Region `
        --service-account "instagram-agent-dev-sa@$ProjectId.iam.gserviceaccount.com" `
        --set-env-vars "GOOGLE_CLOUD_PROJECT=$ProjectId,GCS_BUCKET=$ProjectId-dev-videos,OPENAI_API_KEY=$env:OPENAI_API_KEY" `
        --allow-unauthenticated `
        --memory 1Gi `
        --cpu 1 `
        --min-instances 0 `
        --max-instances 10 `
        --timeout 300 `
        --port 8080
        
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to update Cloud Run service" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Service not found. Please deploy using Terraform first." -ForegroundColor Red
    Write-Host "Run: terraform apply -var-file=terraform.tfvars" -ForegroundColor Yellow
    exit 1
}

# Get service URL
$ServiceUrl = gcloud run services describe $ServiceName --region=$Region --format="value(status.url)"

Write-Host ""
Write-Host "=== Deployment Successful! ===" -ForegroundColor Green
Write-Host "Service URL: $ServiceUrl" -ForegroundColor Cyan
Write-Host "Image: $FullImageName" -ForegroundColor Cyan

# Test the deployment
Write-Host ""
Write-Host "Testing deployment..." -ForegroundColor Yellow
try {
    $Response = Invoke-RestMethod -Uri $ServiceUrl -Method Get -TimeoutSec 30
    Write-Host "✅ Health check passed" -ForegroundColor Green
    Write-Host "Response: $($Response | ConvertTo-Json -Compress)" -ForegroundColor Cyan
}
catch {
    Write-Host "⚠️ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "The service may still be starting up. Please check manually: $ServiceUrl" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Green
Write-Host "• View logs: gcloud run logs tail $ServiceName --region=$Region" -ForegroundColor White
Write-Host "• Monitor: https://console.cloud.google.com/run/detail/$Region/$ServiceName" -ForegroundColor White
Write-Host "• Test endpoints:" -ForegroundColor White
Write-Host "  - Health: $ServiceUrl/health" -ForegroundColor White
Write-Host "  - Web UI: $ServiceUrl" -ForegroundColor White
Write-Host "  - Query API: $ServiceUrl/query (POST)" -ForegroundColor White