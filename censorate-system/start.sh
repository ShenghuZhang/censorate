#!/bin/bash

# Stratos Management System - Development Startup Script

echo "🚀 Starting Stratos Management System..."
echo ""

# Check Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python -c "from backend.database import init_db; init_db()"
echo "✅ Database initialized."
echo ""

# Start backend and frontend
echo "🌐 Starting backend server on http://localhost:8216..."
echo "🌐 Frontend files served from ./frontend"
echo ""
echo "📚 API Documentation: http://localhost:8216/docs"
echo "📚 Frontend: http://localhost:8216/static/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start FastAPI (this will serve static frontend files too)
python3 run_server.py
