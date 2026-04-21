@echo off
REM ==================================
REM Start Backend Server
REM ==================================
echo.
echo =====================================
echo  Starting Goa Heritage AI Backend...
echo =====================================
echo.

cd /d C:\Users\user\Downloads\final-year-main\final-year-main\backend\app

echo Installing dependencies...
pip install -r requirements.txt > nul 2>&1

echo.
echo Starting Python server on port 9000...
echo.
python main.py

pause
