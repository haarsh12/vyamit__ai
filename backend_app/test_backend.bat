@echo off
echo 🧪 Testing Vyamit AI Backend...
echo ================================

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo ✅ Virtual environment activated
echo 🔍 Testing all endpoints...
echo.

python test_endpoints.py

echo.
echo 🔍 Testing database connection...
python test_connection.py

echo.
echo 🔍 Verifying configuration...
python verify_config.py

pause