#!/bin/bash

# NiveshakAI Simple Startup Script (without Docker)

echo "🚀 Starting NiveshakAI (Virtual Environment Mode)..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one with your OpenAI API key:"
    echo "   echo 'OPENAI_API_KEY=your_api_key_here' > .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/annual_reports data/books data/uploads reports logs data/embeddings data/qdrant_storage

# Check if Qdrant is running (optional)
if command -v curl &>/dev/null; then
    if curl -s http://localhost:6333 >/dev/null 2>&1; then
        echo "✅ Qdrant is running on port 6333"
    else
        echo "⚠️  Qdrant not detected. Vector operations will use in-memory storage."
    fi
fi

# Stop any existing Flask processes
pkill -f "python.*app.py" 2>/dev/null || true

# Start the web application
echo "🌐 Starting web server..."
echo ""
echo "📊 NiveshakAI Web Interface will be available at:"
echo "   🏠 Home: http://localhost:5000"
echo "   🔍 Analysis: http://localhost:5000/analyze"
echo "   📁 Upload: http://localhost:5000/upload"
echo "   📊 Reports: http://localhost:5000/reports"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Set environment variables
export PYTHONPATH=$PWD
export FLASK_APP=app.py

# Run the application
python app.py
