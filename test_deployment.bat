@echo off
echo JobHatch Backend Deployment Test
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if requests module is installed
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing requests module...
    pip install requests
)

REM Run the test script
echo Running deployment test...
echo.
python test_deployment.py

echo.
echo Test completed. Press any key to exit...
pause >nul 