@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Python environment not found. Follow README.md first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "server.py"
if errorlevel 1 pause
