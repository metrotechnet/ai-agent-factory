#!/bin/bash
# Ben Nutritionist AI Deployment Script for Linux/macOS
# This script builds and deploys the Ben Nutritionist AI assistant to Google Cloud Run

set -e  # Exit on any error

# Default configuration
TAG=${TAG:-"latest"}
PROJECT_ID=${PROJECT_ID:-"bennutritioniste-ai"}
REGION=${REGION:-"us-east4"}
SERVICE_NAME=${SERVICE_NAME:-"ben-nutritionist"}
SKIP_BUILD=${SKIP_BUILD:-"false"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Show help
show_help() {
    echo -e "${GREEN}Ben Nutritionist AI Deployment Script${NC}"
    echo ""
    echo "Usage: ./deploy.sh [OPTIONS]"
    echo ""
    echo "Environment Variables:"
    echo "  TAG                 Docker image tag (default: latest)"
    echo "  PROJECT_ID          Google Cloud project ID (default: bennutritioniste-ai)"
    echo "  REGION              Google Cloud region (default: us-east4)"
    echo "  SERVICE_NAME        Cloud Run service name (default: ben-nutritionist)"
    echo "  SKIP_BUILD          Skip building the Docker image (default: false)"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh                           # Build and deploy with defaults"
    echo "  TAG=v1.2.3 ./deploy.sh               # Deploy with specific tag"
    echo "  SKIP_BUILD=true ./deploy.sh          # Only update Cloud Run service"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        *)
            echo "Unknown option $1"
            show_help
            ;;
    esac
done

# Configuration
IMAGE_NAME="$REGION-docker.pkg.dev/$PROJECT_ID/$PROJECT_ID-docker-repo/ben-nutritionist"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

echo -e "${GREEN}=== Ben Nutritionist AI Deployment ===${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "Image: $FULL_IMAGE_NAME"
echo "Skip Build: $SKIP_BUILD"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo -e "${GREEN}✅ Environment variables loaded from .env${NC}"
else
    echo -e "${YELLOW}⚠️ No .env file found - make sure OPENAI_API_KEY is set${NC}"
fi

if ! command_exists gcloud; then
    echo -e "${RED}❌ Google Cloud CLI (gcloud) not found. Please install it first.${NC}"
    exit 1
fi

if ! command_exists docker && [ "$SKIP_BUILD" != "true" ]; then
    echo -e "${RED}❌ Docker not found. Please install Docker or set SKIP_BUILD=true.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Check authentication
echo -e "${YELLOW}Checking Google Cloud authentication...${NC}"
AUTH_CHECK=$(gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>/dev/null || echo "")
if [ -z "$AUTH_CHECK" ]; then
    echo -e "${RED}❌ Not authenticated with Google Cloud. Please run: gcloud auth login${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Authenticated as: $AUTH_CHECK${NC}"

# Set project
echo -e "${YELLOW}Setting project to $PROJECT_ID...${NC}"
gcloud config set project "$PROJECT_ID"

# Build and push Docker image
if [ "$SKIP_BUILD" != "true" ]; then
    echo -e "${YELLOW}Building and pushing Docker image...${NC}"
    
    # Use Cloud Build for building
    echo -e "${CYAN}Using Google Cloud Build to build image...${NC}"
    gcloud builds submit --tag "$FULL_IMAGE_NAME" .
    
    echo -e "${GREEN}✅ Image built and pushed successfully${NC}"
else
    echo -e "${YELLOW}⏭️ Skipping build step${NC}"
fi

# Check if service exists
echo -e "${YELLOW}Checking if Cloud Run service exists...${NC}"
SERVICE_EXISTS=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(metadata.name)" 2>/dev/null || echo "")

if [ -n "$SERVICE_EXISTS" ]; then
    echo -e "${YELLOW}Updating existing Cloud Run service...${NC}"
    
    # Update the service
    gcloud run deploy "$SERVICE_NAME" \
        --image "$FULL_IMAGE_NAME" \
        --region "$REGION" \
        --service-account "instagram-agent-dev-sa@$PROJECT_ID.iam.gserviceaccount.com" \
        --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCS_BUCKET=$PROJECT_ID-dev-videos,OPENAI_API_KEY=$OPENAI_API_KEY" \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10 \
        --timeout 300 \
        --port 8080
else
    echo -e "${RED}Service not found. Please deploy using Terraform first.${NC}"
    echo -e "${YELLOW}Run: terraform apply -var-file=terraform.tfvars${NC}"
    exit 1
fi

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")

echo ""
echo -e "${GREEN}=== Deployment Successful! ===${NC}"
echo -e "${CYAN}Service URL: $SERVICE_URL${NC}"
echo -e "${CYAN}Image: $FULL_IMAGE_NAME${NC}"

# Test the deployment
echo ""
echo -e "${YELLOW}Testing deployment...${NC}"
if curl -s --max-time 30 "$SERVICE_URL" >/dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    RESPONSE=$(curl -s "$SERVICE_URL")
    echo -e "${CYAN}Response: $RESPONSE${NC}"
else
    echo -e "${RED}⚠️ Health check failed${NC}"
    echo -e "${YELLOW}The service may still be starting up. Please check manually: $SERVICE_URL${NC}"
fi

echo ""
echo -e "${GREEN}=== Next Steps ===${NC}"
echo -e "${WHITE}• View logs: gcloud run logs tail $SERVICE_NAME --region=$REGION${NC}"
echo -e "${WHITE}• Monitor: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME${NC}"
echo -e "${WHITE}• Test endpoints:${NC}"
echo -e "${WHITE}  - Health: $SERVICE_URL/health${NC}"
echo -e "${WHITE}  - Web UI: $SERVICE_URL${NC}"
echo -e "${WHITE}  - Query API: $SERVICE_URL/query (POST)${NC}"