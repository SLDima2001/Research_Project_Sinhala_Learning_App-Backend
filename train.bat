@echo off
REM Sinhala Handwriting Recognition Model Training Script
REM This script trains the AI model for Sinhala handwriting recognition

echo.
echo ========================================================================
echo SINHALA HANDWRITING RECOGNITION - MODEL TRAINING
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import tensorflow; import cv2; import numpy; import sklearn" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing required packages...
    echo This may take a few minutes...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
)

echo.
echo ========================================================================
echo Starting model training...
echo ========================================================================
echo.

REM Run the training script
python train_sinhala_model.py

if errorlevel 1 (
    echo.
    echo ERROR: Training failed
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo Training completed successfully!
echo ========================================================================
echo.
echo Check the 'models' folder for:
echo   - sinhala_model.keras (trained model)
echo   - sinhala_model_info.json (model information)
echo   - sinhala_model_history.json (training history)
echo   - training_history.png (performance visualization)
echo.
pause
