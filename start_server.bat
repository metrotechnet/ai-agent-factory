@echo off
echo Starting Personal AI Agent Server...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000

pause
