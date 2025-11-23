# Start Personal AI Agent Server
Write-Host "Starting Personal AI Agent Server..." -ForegroundColor Green
Write-Host ""

# Start the server using venv python directly
Write-Host "Starting uvicorn server..." -ForegroundColor Cyan
& ".\venv\Scripts\python.exe" -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
