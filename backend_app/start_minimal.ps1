# Minimal PowerShell script to start FastAPI server
& ".\venv\Scripts\Activate.ps1"
Set-Location app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload