@echo off
REM Sinhala Handwriting Recognition - Windows Setup Script
REM Run this file to automatically set up the environment

echo ============================================================
echo SINHALA HANDWRITING RECOGNITION - SETUP
echo ============================================================
echo.

REM Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9-3.12 from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo OK: Python is installed
echo.

REM Check Python version
echo [2/5] Checking Python version...
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%
echo.

REM Create virtual environment (optional but recommended)
echo [3/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo OK: Virtual environment created
) else (
    echo OK: Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [4/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo OK: Virtual environment activated
echo.

REM Install requirements
echo [5/5] Installing required packages...
echo This may take 5-10 minutes...
echo.
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install some packages
    echo.
    echo Trying alternative installation...
    pip install tensorflow-cpu==2.20.0
    pip install numpy==1.26.4
    pip install opencv-python==4.10.0.84
    pip install Pillow==11.0.0
    pip install scikit-learn==1.5.2
    pip install Flask==3.1.0
    pip install Flask-CORS==5.0.0
)

echo.
echo ============================================================
echo SETUP COMPLETE!
echo ============================================================
echo.
echo Next steps:
echo   1. Prepare your dataset: python prepare_dataset.py
echo   2. Train the model: python train_model.py
echo   3. Start the API: python app.py
echo   4. Test the API: python test_api.py --quick
echo.
echo To activate virtual environment in future:
echo   venv\Scripts\activate.bat
echo.
pause