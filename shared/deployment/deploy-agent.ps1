#!/usr/bin/env powershell
# Universal AI Agent Deployment Script
# Deploys any agent to any environment with consistent configuration

param(
    [string]$AgentName = "",
    [string]$Environment = "dev",
    [string]$Tag = "latest",
    [string]$ProjectId = "",
    [string]$Region = "us-east4",
    [switch]$SkipBuild = $false,
    [switch]$Help = $false
)

# Show help
if ($Help -or $AgentName -eq "") {
    Write-Host "Universal AI Agent Deployment Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\deploy-agent.ps1 -AgentName <name> [OPTIONS]"
    Write-Host ""
    Write-Host "Required:"
    Write-Host "  -AgentName <string>    Agent to deploy (ben-nutritionist, fitness-coach, etc.)"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Environment <string>  Environment (dev, staging, production)"
    Write-Host "  -Tag <string>         Docker image tag (default: latest)"
    Write-Host "  -ProjectId <string>   GCP project ID (auto-detected if not provided)"
    Write-Host "  -Region <string>      GCP region (default: us-east4)"
    Write-Host "  -SkipBuild           Skip building the Docker image"
    Write-Host "  -Help                Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy-agent.ps1 -AgentName ben-nutritionist"
    Write-Host "  .\deploy-agent.ps1 -AgentName fitness-coach -Environment production -Tag v1.2.0"
    Write-Host "  .\deploy-agent.ps1 -AgentName wellness-therapist -SkipBuild"
    exit 0
}

# Validate agent exists
$AgentPath = "agents\$AgentName"
if (!(Test-Path $AgentPath)) {
    Write-Host "❌ Agent '$AgentName' not found in $AgentPath" -ForegroundColor Red
    Write-Host "Available agents:" -ForegroundColor Yellow
    Get-ChildItem "agents" -Directory | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
    exit 1
}

# Auto-detect project ID if not provided
if ($ProjectId -eq "") {
    $ProjectId = gcloud config get-value project 2>$null
    if ($ProjectId -eq "") {
        Write-Host "❌ Could not detect GCP project. Please provide -ProjectId" -ForegroundColor Red
        exit 1
    }
}

# Configuration
$TerraformPath = "infrastructure\terraform\projects\$AgentName"
$ImageName = "$Region-docker.pkg.dev/$ProjectId/agents/$AgentName"
$FullImageName = "${ImageName}:${Tag}"

Write-Host "=== Universal Agent Deployment ===" -ForegroundColor Green
Write-Host "Agent: $AgentName" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Cyan
Write-Host "Project ID: $ProjectId" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Cyan
Write-Host "Image: $FullImageName" -ForegroundColor Cyan
Write-Host ""

# Load agent-specific environment variables
$EnvFile = "$AgentPath\.env"
if (Test-Path $EnvFile) {
    Write-Host "Loading agent-specific environment variables..." -ForegroundColor Yellow
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Build Docker image if not skipping
if (!$SkipBuild) {
    Write-Host "Building Docker image for $AgentName..." -ForegroundColor Yellow
    Push-Location $AgentPath
    
    # Use agent-specific Dockerfile if it exists, otherwise use shared one
    $DockerFile = if (Test-Path "Dockerfile") { "Dockerfile" } else { "..\..\shared\deployment\Dockerfile.template" }
    
    docker build -f $DockerFile -t $FullImageName . --build-arg AGENT_NAME=$AgentName
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker build failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Write-Host "Pushing image to Artifact Registry..." -ForegroundColor Yellow
    docker push $FullImageName
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker push failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Pop-Location
    Write-Host "✅ Image built and pushed successfully" -ForegroundColor Green
}

# Deploy infrastructure with Terraform
if (Test-Path $TerraformPath) {
    Write-Host "Deploying infrastructure..." -ForegroundColor Yellow
    Push-Location $TerraformPath
    
    # Initialize Terraform if needed
    if (!(Test-Path ".terraform")) {
        terraform init
    }
    
    # Apply with environment-specific vars
    $TfVarsFile = "$Environment.tfvars"
    if (!(Test-Path $TfVarsFile)) {
        $TfVarsFile = "terraform.tfvars"
    }
    
    # Update container image in tfvars
    $TfVars = Get-Content $TfVarsFile -Raw
    $TfVars = $TfVars -replace 'container_image\s*=\s*"[^"]*"', "container_image = `"$FullImageName`""
    Set-Content $TfVarsFile $TfVars
    
    terraform apply -var-file=$TfVarsFile -auto-approve
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Terraform deployment failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    # Get service URL
    $ServiceUrl = terraform output -raw service_url 2>$null
    Pop-Location
    
    Write-Host "✅ Infrastructure deployed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ No Terraform configuration found for $AgentName" -ForegroundColor Yellow
    $ServiceUrl = "https://$AgentName-$ProjectId.run.app"
}

# Test deployment
Write-Host ""
Write-Host "Testing deployment..." -ForegroundColor Yellow
try {
    $Response = Invoke-RestMethod -Uri "$ServiceUrl/health" -Method Get -TimeoutSec 30
    Write-Host "✅ Health check passed" -ForegroundColor Green
    Write-Host "Agent: $($Response.service)" -ForegroundColor Cyan
    Write-Host "Version: $($Response.version)" -ForegroundColor Cyan
    Write-Host "Specialization: $($Response.specialization)" -ForegroundColor Cyan
    Write-Host "Features: $($Response.features -join ', ')" -ForegroundColor Cyan
}
catch {
    Write-Host "⚠️ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Deployment Complete! ===" -ForegroundColor Green
Write-Host "Agent URL: $ServiceUrl" -ForegroundColor Cyan
Write-Host "Management: https://console.cloud.google.com/run/detail/$Region/$AgentName" -ForegroundColor White