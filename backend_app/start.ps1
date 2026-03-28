#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Single command to start the backend server with virtual environment activation
.DESCRIPTION
    This script activates the virtual environment and starts the FastAPI server
    from the correct directory in one command.
#>

Write-Host "🚀 Starting Backend Server..." -ForegroundColor Green
Write-Host "=" * 40 -ForegroundColor Gray

# Get the script directory (backend_app)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "📁 Working from: $PWD" -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found at venv\Scripts\Activate.ps1" -ForegroundColor Red
    Write-Host "   Please create virtual environment first:" -ForegroundColor Yellow
    Write-Host "   python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Change to app directory
Set-Location "app"
Write-Host "📂 Changed to app directory: $PWD" -ForegroundColor Cyan

# Display server info
Write-Host ""
Write-Host "🌐 Server will be available at: http://localhost:8000" -ForegroundColor Magenta
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Magenta
Write-Host "🔄 Starting uvicorn server..." -ForegroundColor Yellow
Write-Host ""

# Start the server
try {
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}
catch {
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
    exit 1
}