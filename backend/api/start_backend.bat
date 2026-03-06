@echo off
echo ============================================================
echo Starting Sinhala Learning App Backend (Port 5002)
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Start the server
echo.
echo ============================================================
echo Starting Flask-SocketIO server...
echo Server will be accessible at http://localhost:5002
echo ============================================================
echo.
python app.py
