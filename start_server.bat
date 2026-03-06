@echo off
echo ========================================
echo Sinhala Handwriting Recognition Backend
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Get IP address
echo Your IP addresses:
ipconfig | findstr /i "IPv4"
echo.
echo Update your mobile app with one of the above IP addresses!
echo Example: const API_URL = 'http://192.168.1.6:5001';
echo.

REM Start server
echo Starting Flask server...
echo.
python app.py
