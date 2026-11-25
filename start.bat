@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python Launcher "py" was not found.
    echo Install Python 3.11 or newer and enable the Python launcher.
    pause
    exit /b 1
)

py -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    echo Check your internet connection and Python/pip installation.
    pause
    exit /b 1
)

py hui_server.py
set "PROGRAM_EXIT=%errorlevel%"

if not "%PROGRAM_EXIT%"=="0" (
    echo [ERROR] The HUI server stopped with exit code %PROGRAM_EXIT%.
    pause
)

exit /b %PROGRAM_EXIT%
