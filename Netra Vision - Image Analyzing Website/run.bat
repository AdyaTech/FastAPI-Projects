@echo off
rem Starts Netra Vision on Windows at http://localhost:8000
cd /d "%~dp0"
if not exist .venv (
  py -3 -m venv .venv 2>nul || python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
if not exist .env copy .env.example .env >nul
cd app
echo.
echo Netra is starting. Open http://localhost:8000 in your browser.
echo Press Ctrl+C in this window to stop it.
echo.
uvicorn main:app
pause
