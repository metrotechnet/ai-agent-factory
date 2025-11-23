# Test Docker build locally
Write-Host "Building Docker image locally..." -ForegroundColor Green

# Build the image
docker build -t benboulanger-ai:local .

Write-Host "`nTesting locally on port 8080..." -ForegroundColor Cyan
Write-Host "Access at: http://localhost:8080" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Gray

# Run the container
docker run -p 8080:8080 `
  -e OPENAI_API_KEY="$env:OPENAI_API_KEY" `
  -e PORT=8080 `
  benboulanger-ai:local
