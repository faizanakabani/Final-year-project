@echo off
REM ==================================
REM Start Flutter Web App in Chrome
REM ==================================
echo.
echo =====================================
echo  Starting Goa Heritage Flutter App...
echo =====================================
echo.

cd /d C:\Users\user\Downloads\final-year-main\final-year-main\flutterapp

echo Cleaning previous build...
flutter clean > nul 2>&1

echo Getting dependencies...
flutter pub get > nul 2>&1

echo.
echo Building and launching in Chrome...
echo.
flutter run -d chrome

pause
