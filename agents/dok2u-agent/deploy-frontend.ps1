#!/usr/bin/env pwsh
# PowerShell script to deploy Dok2u Frontend to Firebase

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Deploying Dok2u Frontend to Firebase" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Firebase CLI is installed
$firebaseCmd = Get-Command firebase -ErrorAction SilentlyContinue
if (-not $firebaseCmd) {
    Write-Host "ERROR: Firebase CLI is not installed!" -ForegroundColor Red
    Write-Host "Please install it using: npm install -g firebase-tools" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Load backend URL from .env if exists
$backendUrl = "http://localhost:8080"
if (Test-Path ".env") {
    $envContent = Get-Content ".env"
    $backendLine = $envContent | Where-Object { $_ -match "^BACKEND_URL=" }
    if ($backendLine) {
        $backendUrl = ($backendLine -split "=", 2)[1].Trim()
    } else {
        Write-Host "WARNING: BACKEND_URL not found in .env. Using default." -ForegroundColor Yellow
    }
} else {
    Write-Host "WARNING: .env file not found! Using default backend URL." -ForegroundColor Yellow
}

Write-Host "Backend URL: $backendUrl" -ForegroundColor Green
Write-Host ""

# Create public directory structure
Write-Host "Creating public directory structure..." -ForegroundColor Cyan
if (-not (Test-Path "public")) {
    New-Item -ItemType Directory -Path "public" | Out-Null
}
if (-not (Test-Path "public\static")) {
    New-Item -ItemType Directory -Path "public\static" | Out-Null
}

Write-Host "Copying frontend files..." -ForegroundColor Cyan

# Copy index.html from templates
Copy-Item "templates\index.html" "public\index.html" -Force
if (-not $?) {
    Write-Host "ERROR: Failed to copy index.html" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Copy all static files
Copy-Item "static\*" "public\static\" -Recurse -Force
if (-not $?) {
    Write-Host "ERROR: Failed to copy static files" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Update index.html to use correct paths for Firebase hosting
Write-Host "Updating file paths for Firebase hosting..." -ForegroundColor Cyan
$indexContent = Get-Content "public\index.html" -Raw
$indexContent = $indexContent -replace '/static/', 'static/'
Set-Content "public\index.html" -Value $indexContent

# Create a config.js file with backend URL
$configJs = @"
// Backend configuration for Firebase deployment
window.BACKEND_URL = '$backendUrl';
"@
Set-Content "public\static\config.js" -Value $configJs

Write-Host ""
Write-Host "Files prepared successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Choose deployment option:" -ForegroundColor Cyan
Write-Host "1. Deploy to Firebase Hosting"
Write-Host "2. Preview locally (Firebase emulator)"
Write-Host "3. Exit"
Write-Host ""
$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Deploying to Firebase Hosting..." -ForegroundColor Cyan
        firebase deploy --only hosting
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "====================================" -ForegroundColor Green
            Write-Host "Deployment successful!" -ForegroundColor Green
            Write-Host "====================================" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "ERROR: Deployment failed!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    "2" {
        Write-Host ""
        Write-Host "Starting Firebase emulator..." -ForegroundColor Cyan
        firebase emulators:start --only hosting
    }
    default {
        Write-Host ""
        Write-Host "Deployment cancelled." -ForegroundColor Yellow
    }
}

Write-Host ""
Read-Host "Press Enter to exit"
