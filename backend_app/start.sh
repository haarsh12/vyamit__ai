#!/bin/bash
# Single command to start the backend server with virtual environment activation

echo "🚀 Starting Backend Server..."
echo "========================================"

# Get script directory and change to it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working from: $PWD"

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Virtual environment not found at venv/bin/activate"
    echo "   Please create virtual environment first:"
    echo "   python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"

# Change to app directory
cd app
echo "📂 Changed to app directory: $PWD"

echo ""
echo "🌐 Server will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔄 Starting uvicorn server..."
echo ""

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload