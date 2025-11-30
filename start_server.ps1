# Start Personal AI Agent Server
Write-Host "Starting Ben Boulanger AI Agent Server..." -ForegroundColor Green
Write-Host ""

# Check if env exists, fallback to venv
$envPath = if (Test-Path ".\env\Scripts\python.exe") { ".\env" } else { ".\venv" }

if (-Not (Test-Path "$envPath\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found. Creating..." -ForegroundColor Red
    python -m venv env
    $envPath = ".\env"
    Write-Host "✅ Virtual environment created." -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "Activating virtual environment ($envPath)..." -ForegroundColor Cyan
& "$envPath\Scripts\Activate.ps1"

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
$uvicornCheck = & "$envPath\Scripts\python.exe" -c "import uvicorn; print('OK')" 2>$null
if ($uvicornCheck -ne "OK") {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & "$envPath\Scripts\python.exe" -m pip install -r requirements.txt
    Write-Host "✅ Dependencies installed." -ForegroundColor Green
}

# Start the server
Write-Host "Starting uvicorn server on http://localhost:8001..." -ForegroundColor Cyan
Write-Host ""
& "$envPath\Scripts\python.exe" app.py

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
