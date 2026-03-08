@echo off
REM Universal Crawler Startup Script
REM ================================

echo Starting Universal Crawler...

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Start the API server
python universal_crawler_api.py
