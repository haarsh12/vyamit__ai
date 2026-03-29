#!/usr/bin/env pwsh
# 🚀 VECTOR RAG SETUP SCRIPT
# This script sets up the complete vector RAG system

Write-Host "🚀 VECTOR RAG SYSTEM SETUP" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️ Virtual environment not detected!" -ForegroundColor Yellow
    Write-Host "📋 Activating virtual environment..." -ForegroundColor Cyan
    
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & ".venv\Scripts\Activate.ps1"
        Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
    } elseif (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
        Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
    } else {
        Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
        Write-Host "📋 Please create a virtual environment first:" -ForegroundColor Yellow
        Write-Host "   python -m venv .venv" -ForegroundColor White
        Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor White
        exit 1
    }
}

Write-Host "📦 Installing required packages..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "`n🔍 Checking installation..." -ForegroundColor Cyan
python -c "
import sentence_transformers
import sqlalchemy
import psycopg2
import numpy
print('✅ All packages installed successfully!')
"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n🎉 Setup completed successfully!" -ForegroundColor Green
    Write-Host "📋 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Make sure your Supabase database is set up" -ForegroundColor White
    Write-Host "   2. Run the SQL setup: backend_app/supabase_vector_setup.sql" -ForegroundColor White
    Write-Host "   3. Test the system: python test_complete_vector_rag.py" -ForegroundColor White
    Write-Host "`n🚀 Ready to run Vector RAG system!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Setup failed! Please check the error messages above." -ForegroundColor Red
    exit 1
}