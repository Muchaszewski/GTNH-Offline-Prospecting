@echo off
title GTNH Offline Prospector Server
echo Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! 
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b
)

if not exist venv (
    echo Creating an isolated Virtual Environment ^(venv^)...
    python -m venv venv
)

echo Activating environment...
call venv\Scripts\activate

echo Installing necessary dependencies...
pip install -q -r requirements.txt

echo Starting server...
echo -----------------------------------------------------
echo Go to http://127.0.0.1:5050/ in your web browser!
echo -----------------------------------------------------
python app.py
pause
