@echo off
REM Quick run script for Sinhala Handwriting Recognition API

echo ============================================================
echo SINHALA HANDWRITING RECOGNITION API - STARTING
echo ============================================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Check if model exists
if exist "models\sinhala_model.keras" (
    echo Model found: models\sinhala_model.keras
    echo Running in TRAINED MODEL mode
) else (
    echo WARNING: No trained model found!
    echo Running in MOCK MODE
    echo.
    echo To train the model:
    echo   1. python prepare_dataset.py
    echo   2. python train_model.py
)

echo.
echo Starting Flask API...
echo API will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

python app.py

pause