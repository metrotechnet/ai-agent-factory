# Instagram Agent - Quick Build & Deploy Scripts
# ==============================================

## Windows PowerShell Script (deploy.ps1)

**Usage:**
```powershell
# Basic deployment
.\deploy.ps1

# Deploy with specific tag
.\deploy.ps1 -Tag v1.2.3

# Skip building (only update service)
.\deploy.ps1 -SkipBuild

# Show help
.\deploy.ps1 -Help
```

**Options:**
- `-Tag <string>`: Docker image tag (default: latest)
- `-ProjectId <string>`: Google Cloud project ID (default: bennutritioniste-ai)
- `-Region <string>`: Google Cloud region (default: us-east4)
- `-ServiceName <string>`: Cloud Run service name (default: instagram-agent)
- `-SkipBuild`: Skip building the Docker image
- `-Help`: Show help message

## Linux/macOS Shell Script (deploy.sh)

**Usage:**
```bash
# Basic deployment
./deploy.sh

# Deploy with specific tag
TAG=v1.2.3 ./deploy.sh

# Skip building (only update service)
SKIP_BUILD=true ./deploy.sh

# Show help
./deploy.sh --help
```

**Environment Variables:**
- `TAG`: Docker image tag (default: latest)
- `PROJECT_ID`: Google Cloud project ID (default: bennutritioniste-ai)
- `REGION`: Google Cloud region (default: us-east4)
- `SERVICE_NAME`: Cloud Run service name (default: instagram-agent)
- `SKIP_BUILD`: Skip building the Docker image (default: false)

## What These Scripts Do

1. **Validate Prerequisites**: Check for gcloud CLI and Docker
2. **Authenticate**: Verify Google Cloud authentication
3. **Build Image**: Use Google Cloud Build to create Docker image
4. **Deploy**: Update the Cloud Run service with new image
5. **Test**: Perform health check on deployed service
6. **Report**: Show deployment status and next steps

## Quick Start

For Windows:
```powershell
.\deploy.ps1
```

For Linux/macOS:
```bash
./deploy.sh
```

## Prerequisites

- Google Cloud CLI (`gcloud`) installed and authenticated
- Docker installed (if not using Cloud Build)
- Terraform infrastructure already deployed