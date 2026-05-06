@echo off
REM Quick Setup Script for Stress Prediction System (Windows)
REM Run this script to set up and start the web application

echo ==========================================
echo \ud83e\udde0 Stress Prediction System Setup
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Install dependencies
echo Installing dependencies...
cd web_app
pip install -r requirements.txt
cd ..
echo ✓ Dependencies installed
echo.

REM Check if model exists
if not exist "web_app\best_model.joblib" (
    echo ⚠️  Model not found. Training initial model...
    echo This may take 5-10 minutes depending on your system...
    echo.
    python train_model.py
    if errorlevel 1 (
        echo.
        echo ❌ Training failed. Please check the error above.
        exit /b 1
    )
    echo.
    echo ✓ Initial training complete!
) else (
    echo ✓ Model already exists
)

echo.
echo ==========================================
echo 🚀 Starting Web Application
echo ==========================================
echo.
echo Open your browser and go to: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo.

cd web_app
python app.py
