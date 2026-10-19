@echo off
echo ==================================================
echo   Starting PayManagement Servers...
echo ==================================================

echo 1. Starting Flask Backend API (Port 5000)...
start "PayManagement Backend" cmd /k "cd /d %~dp0 && python app.py"

echo 2. Starting React Frontend (Port 5174)...
start "PayManagement Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo Both servers have been launched in separate windows!
echo - Keep those black windows open while using the app.
echo - Your React App will be available at: http://localhost:5174/
echo.
pause
