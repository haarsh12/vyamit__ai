@echo off
echo 🚀 Starting Backend Server...
echo ========================================

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found at venv\Scripts\activate.bat
    echo    Please create virtual environment first:
    echo    python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo 📁 Working from: %CD%

REM Change to app directory
cd app
echo 📂 Changed to app directory: %CD%

echo.
echo 🌐 Server will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo 🔄 Starting uvicorn server...
echo ⚠️  Keep this window open while server is running!
echo.

REM Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause