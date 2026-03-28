@echo off
echo 🚀 Starting Vyamit AI Backend Server...
echo ==========================================

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo ✅ Virtual environment activated
echo 📁 Current directory: %CD%
echo 🌐 Server will be available at: http://127.0.0.1:8000
echo 📚 API Documentation: http://127.0.0.1:8000/docs
echo.
echo 🔄 Starting server with database connection...
echo ⚠️  Keep this window open while testing!
echo.

cd app
python main_with_db.py

pause