@echo off
REM ====================================
REM Upload ChromaDB files to GCS bucket
REM ====================================
echo.

REM Load configuration from .env file
if not exist ".env" (
    echo ERROR: .env file not found!
    pause
    exit /b 1
)

for /f "tokens=1,2 delims==" %%a in ('findstr /b "GCP_PROJECT_ID=" .env') do set GCP_PROJECT_ID=%%b

if "%GCP_PROJECT_ID%"=="" (
    echo ERROR: GCP_PROJECT_ID not found in .env file!
    pause
    exit /b 1
)

set BUCKET_NAME=agent-factory-database
set KB_DIR=knowledge-base

echo ====================================
echo Uploading ChromaDB to gs://%BUCKET_NAME%
echo Project: %GCP_PROJECT_ID%
echo ====================================
echo.

REM Loop through each project in knowledge-base/
for /d %%P in (%KB_DIR%\*) do (
    set "PROJECT=%%~nxP"
    setlocal enabledelayedexpansion
    if exist "%%P\chroma_db" (
        echo Clearing gs://%BUCKET_NAME%/!PROJECT!/chroma_db ...
        call gcloud storage rm "gs://%BUCKET_NAME%/!PROJECT!/chroma_db/**" --recursive 2>nul
        echo Uploading !PROJECT!/chroma_db ...
        call gcloud storage cp "%%P\chroma_db" "gs://%BUCKET_NAME%/!PROJECT!/chroma_db" --recursive
        if errorlevel 1 (
            echo ERROR: Failed to upload !PROJECT!/chroma_db
            endlocal
        ) else (
            echo OK: !PROJECT!/chroma_db uploaded.
            endlocal
        )
    ) else (
        echo SKIP: !PROJECT! has no chroma_db folder.
        endlocal
    )
)

echo.
echo ====================================
echo Upload complete.
echo ====================================
pause
