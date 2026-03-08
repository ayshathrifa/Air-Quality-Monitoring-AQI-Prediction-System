@echo off
echo ========================================
echo Air Quality Monitoring System - Setup
echo ========================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
echo.

echo Step 2: Training ML model...
python model_trainer.py
echo.

echo Step 3: Starting the application...
echo.
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
