@echo off
setlocal enabledelayedexpansion
echo [DEBUG] Started
echo ====================================
echo Deploying IMX Frontend to Firebase
echo ====================================
echo.

REM Check if Firebase CLI is installed
where firebase >nul 2>nul
if !errorlevel! neq 0 (
    echo ERROR: Firebase CLI is not installed!
    echo Please install it using: npm install -g firebase-tools
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    exit /b 1
)

REM Load Firebase project ID from .env
for /f "tokens=1,2 delims==" %%a in ('findstr /b "FIREBASE_PROJECT_ID=" .env') do set FIREBASE_PROJECT=%%b
if "!FIREBASE_PROJECT!"=="" (
    echo ERROR: FIREBASE_PROJECT_ID not found in .env file!
    exit /b 1
)

echo Setting Firebase project to: !FIREBASE_PROJECT!
call firebase use !FIREBASE_PROJECT!
if !errorlevel! neq 0 (
    echo ERROR: Failed to set Firebase project!
    exit /b 1
)
echo.

REM Load backend URL
for /f "tokens=1,2 delims==" %%a in ('findstr /b "BACKEND_URL=" .env 2^>nul') do set BACKEND_URL=%%b
if "!BACKEND_URL!"=="" if exist ".backend-url.tmp" set /p BACKEND_URL=<.backend-url.tmp
if "!BACKEND_URL!"=="" set BACKEND_URL=http://localhost:8080

echo Backend URL: !BACKEND_URL!
echo.

REM Create and copy files
if not exist "public" mkdir public
if not exist "public\static" mkdir public\static

copy /Y "templates\index.html" "public\index.html" >nul
if !errorlevel! neq 0 (
    echo ERROR: Failed to copy index.html
    exit /b 1
)

xcopy /Y /E /I "static\*" "public\static\" >nul
if !errorlevel! neq 0 (
    echo ERROR: Failed to copy static files
    exit /b 1
)

powershell -Command "(Get-Content 'public\index.html') -replace '/static/', 'static/' | Set-Content 'public\index.html'"
echo window.BACKEND_URL = '!BACKEND_URL!'; > "public\static\js\backend-url.js"

echo Files prepared successfully!
echo.
echo Deploying to Firebase...
call firebase deploy --only hosting
if !errorlevel! equ 0 (
    echo.
    echo Deployment successful!
) else (
    echo.
    echo ERROR: Deployment failed!
    exit /b 1
)
