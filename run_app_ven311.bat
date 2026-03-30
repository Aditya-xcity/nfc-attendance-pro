@echo off
REM Activate Python venv (venv311), run app.py, and open localhost in browser

REM Change to script directory
cd /d %~dp0

REM Activate the virtual environment
call venv311\Scripts\activate.bat

REM Run Flask app in a new window
start cmd /k python app.py

REM Wait a bit so server starts
timeout /t 3 >nul

REM Open browser
start http://127.0.0.1:5000