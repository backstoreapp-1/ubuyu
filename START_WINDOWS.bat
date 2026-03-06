@echo off
REM Ubuyu Marketplace - Start Script for Windows

echo.
echo 🍬 Ubuyu Marketplace - Starting Server...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt > nul 2>&1

REM Start the application
echo.
echo ✅ Server starting on http://localhost:5000
echo.
echo Default Pages:
echo   - Home: http://localhost:5000
echo   - Products: http://localhost:5000/products/catalog
echo   - Register: http://localhost:5000/auth/register
echo   - Login: http://localhost:5000/auth/login
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
pause
