#!/bin/bash
# Quick Setup Script for Stress Prediction System
# Run this script to set up and start the web application

echo "=========================================="
echo "🧠 Stress Prediction System Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Install dependencies
echo "Installing dependencies..."
cd web_app
pip3 install -r requirements.txt
cd ..
echo "✓ Dependencies installed"
echo ""

# Check if model exists
if [ ! -f "web_app/best_model.joblib" ]; then
    echo "⚠️  Model not found. Training initial model..."
    echo "This may take 5-10 minutes depending on your system..."
    echo ""
    python3 train_model.py
    
    # Check if training succeeded
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Initial training complete!"
    else
        echo ""
        echo "❌ Training failed. Please check the error above."
        exit 1
    fi
else
    echo "✓ Model already exists"
fi

echo ""
echo "=========================================="
echo "🚀 Starting Web Application"
echo "=========================================="
echo ""
echo "Open your browser and go to: http://127.0.0.1:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd web_app
python3 app.py
