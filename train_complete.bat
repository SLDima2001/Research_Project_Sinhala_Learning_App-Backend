@echo off
REM Sinhala Handwriting Recognition - Complete Training Script
REM This script will train the model with all dependencies

echo.
echo ========================================================================
echo SINHALA HANDWRITING RECOGNITION - MODEL TRAINING
echo ========================================================================
echo.

REM Set Python path
set PYTHONPATH=%CD%

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import tensorflow; import cv2; import numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies (this may take 5-10 minutes)...
    pip install -q tensorflow opencv-python numpy pillow scikit-learn matplotlib
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo ========================================================================
echo Starting Model Training
echo ========================================================================
echo.
echo Dataset: 454 Sinhala character classes
echo Training images: 26,000+
echo Model: CNN with 4 convolutional blocks
echo Epochs: 100
echo Batch size: 32
echo.
echo This will take approximately 2-4 hours on CPU
echo.

REM Run training
python train_sinhala_model.py

if errorlevel 1 (
    echo.
    echo ERROR: Training failed
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo Training Completed Successfully!
echo ========================================================================
echo.
echo Model saved to: models/sinhala_model.keras
echo.
echo Next steps:
echo 1. Check models/training_history.png for performance graphs
echo 2. Run: python test_model.py (to test the model)
echo 3. Run: python app.py (to start the Flask API)
echo.
pause
