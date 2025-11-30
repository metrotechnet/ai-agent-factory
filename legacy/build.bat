@echo off
echo ====================================
echo Building Ben Boulanger AI Agent
echo ====================================
echo.

REM Advanced cleanup to prevent gcloud conflicts
echo [Pre-build] Performing deep cleanup...
taskkill /f /im gcloud.exe 2>nul
taskkill /f /im python.exe /fi "COMMANDLINE eq *gcloud*" 2>nul
timeout /t 2 /nobreak >nul

REM Force cleanup of all gcloud temp directories
for /d %%i in ("%TEMP%\gcloud_build_*") do rmdir /s /q "%%i" 2>nul
for /d %%i in ("%TEMP%\tmp*") do rmdir /s /q "%%i" 2>nul
del /q /s "%TEMP%\tmp*.tgz" 2>nul

REM Create isolated environment
set CLOUDSDK_PYTHON_SITEPACKAGES=1
set CLOUDSDK_CORE_DISABLE_USAGE_REPORTING=true
set TMPDIR=C:\temp\gcloud_isolated_%TIME:~-5,2%%TIME:~-2,2%
set TEMP=%TMPDIR%
set TMP=%TMPDIR%
mkdir "%TMPDIR%" 2>nul
echo Isolated temp directory: %TMPDIR%
echo.

REM Load environment variables from .env file (don't expose API key in script)
if exist .env (
    echo [Config] Loading environment variables from .env...
    for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a"=="REM" set %%a=%%b
    )
) else (
    echo WARNING: .env file not found! Make sure OPENAI_API_KEY is set.
)

echo [1/3] Validating project structure...
if not exist "Dockerfile" (
    echo ERROR: Dockerfile not found!
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found!
    pause
    exit /b 1
)

if not exist "app.py" (
    echo ERROR: app.py not found!
    pause
    exit /b 1
)

echo [2/3] Building Docker image with Cloud Build...
echo Project: benboulanger-ai
echo Image: gcr.io/benboulanger-ai/benboulanger-ai
echo Machine: e2-highcpu-8 (for faster builds)
echo Timeout: 30 minutes
echo.

REM Try gcloud build with retry mechanism
set /a attempt=1
:retry_build
echo Attempt %attempt%/3: Starting Cloud Build...

gcloud builds submit --tag gcr.io/benboulanger-ai/benboulanger-ai --timeout=30m --machine-type=e2-highcpu-8

if %ERRORLEVEL% EQU 0 goto build_success

echo.
echo ❌ Build attempt %attempt% failed (Exit code: %ERRORLEVEL%)

if %attempt% LSS 3 (
    set /a attempt+=1
    echo 🔄 Retrying in 5 seconds...
    timeout /t 5 /nobreak >nul
    
    REM Clean up again before retry
    taskkill /f /im gcloud.exe 2>nul
    rmdir /s /q "%TMPDIR%" 2>nul
    set TMPDIR=C:\temp\gcloud_retry_%RANDOM%
    mkdir "%TMPDIR%" 2>nul
    
    goto retry_build
)

echo.
echo ❌ ERROR: All build attempts failed!
echo.
echo 🔍 Troubleshooting tips:
echo - Check gcloud authentication: gcloud auth list  
echo - Verify project settings: gcloud config list
echo - Check Cloud Build API is enabled
echo - Verify billing account is active
echo - Try manual build: gcloud builds submit --tag gcr.io/benboulanger-ai/benboulanger-ai
echo.
pause
exit /b 1

:build_success

echo.
echo ✅ [3/3] Build completed successfully!
echo 🚀 Docker image ready: gcr.io/benboulanger-ai/benboulanger-ai
echo 📋 Next step: Run deploy.bat to deploy to Cloud Run

REM Cleanup isolated temp directory
rmdir /s /q "%TMPDIR%" 2>nul

echo.
pause


