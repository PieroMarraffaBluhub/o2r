@echo off
setlocal

echo Setting up O2Ring Monitor Application...

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.9+ and rerun this script.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

REM Create virtual environment if not exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

echo Setup complete! Starting O2Ring Monitor...
echo.

REM Start the app
python o2ring_ui_real.py

pause 