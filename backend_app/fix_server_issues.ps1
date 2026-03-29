# Fix Server Issues Script
Write-Host "=== Fixing Backend Server Issues ===" -ForegroundColor Cyan

# Navigate to backend directory
Set-Location -Path "backend_app" -ErrorAction SilentlyContinue

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found. Creating one..." -ForegroundColor Red
    python -m venv venv
    Write-Host "✅ Virtual environment created!" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install/upgrade all dependencies
Write-Host "Installing updated dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --upgrade

# Verify critical packages
Write-Host "Verifying critical packages..." -ForegroundColor Yellow
python -c "
try:
    from langchain.memory import ConversationBufferMemory
    print('✅ LangChain memory import working')
except ImportError as e:
    print(f'❌ LangChain memory import failed: {e}')

try:
    import google.generativeai as genai
    print('✅ Google GenerativeAI import working')
except ImportError as e:
    print(f'❌ Google GenerativeAI import failed: {e}')

try:
    from langchain_core.messages import BaseMessage
    print('✅ LangChain core messages import working')
except ImportError as e:
    print(f'❌ LangChain core messages import failed: {e}')
"

Write-Host "=== Fix Complete! ===" -ForegroundColor Green
Write-Host "You can now start the server with:" -ForegroundColor Yellow
Write-Host "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White