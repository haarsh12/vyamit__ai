# Update Dependencies Script
Write-Host "Updating Python dependencies..." -ForegroundColor Green

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip first
python -m pip install --upgrade pip

# Install updated requirements
pip install -r requirements.txt --upgrade

Write-Host "Dependencies updated successfully!" -ForegroundColor Green
Write-Host "You can now start the server with: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Yellow