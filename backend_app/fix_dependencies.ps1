# Complete Dependency Fix Script
Write-Host "=== Fixing All Dependencies ===" -ForegroundColor Cyan

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Uninstall conflicting packages first
Write-Host "Removing conflicting packages..." -ForegroundColor Yellow
pip uninstall -y langchain langchain-core langchain-community langchain-google-genai langchain-huggingface google-genai google-generativeai

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install packages in specific order to avoid conflicts
Write-Host "Installing core packages..." -ForegroundColor Yellow
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0

Write-Host "Installing database packages..." -ForegroundColor Yellow
pip install sqlmodel==0.0.14 sqlalchemy==2.0.23 alembic==1.12.1

Write-Host "Installing auth packages..." -ForegroundColor Yellow
pip install python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 python-multipart==0.0.6

Write-Host "Installing utility packages..." -ForegroundColor Yellow
pip install python-dotenv==1.0.0 httpx==0.25.2 requests==2.31.0 pydantic==2.5.0 pydantic-settings==2.1.0

Write-Host "Installing AI packages in correct order..." -ForegroundColor Yellow
pip install google-generativeai==0.7.2
pip install langchain==0.1.0
pip install langchain-community==0.0.13
pip install langchain-google-genai==1.0.1
pip install langchain-huggingface==0.0.3
pip install faiss-cpu==1.7.4
pip install chromadb==0.4.22

Write-Host "Installing remaining packages..." -ForegroundColor Yellow
pip install python-dateutil==2.8.2 orjson==3.9.10 pytest==7.4.3 pytest-asyncio==0.21.1 black==23.11.0 flake8==6.1.0

# Test imports
Write-Host "Testing imports..." -ForegroundColor Yellow
python -c "
import sys
try:
    from langchain.memory import ConversationBufferMemory
    print('✅ LangChain memory: OK')
except Exception as e:
    print(f'❌ LangChain memory: {e}')
    sys.exit(1)

try:
    import google.generativeai as genai
    print('✅ Google GenerativeAI: OK')
except Exception as e:
    print(f'❌ Google GenerativeAI: {e}')
    sys.exit(1)

try:
    from langchain_core.messages import BaseMessage
    print('✅ LangChain core: OK')
except Exception as e:
    print(f'❌ LangChain core: {e}')
    sys.exit(1)

try:
    from app.db.database import create_db_and_tables
    print('✅ App imports: OK')
except Exception as e:
    print(f'❌ App imports: {e}')
    sys.exit(1)

print('🎉 All imports working!')
"

if ($LASTEXITCODE -eq 0) {
    Write-Host "=== SUCCESS! ===" -ForegroundColor Green
    Write-Host "All dependencies installed and working!" -ForegroundColor Green
    Write-Host "Start server with: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
} else {
    Write-Host "=== FAILED ===" -ForegroundColor Red
    Write-Host "Some imports still failing. Check the errors above." -ForegroundColor Red
}