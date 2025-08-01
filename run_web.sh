#!/bin/bash

# NiveshakAI Web Application Startup Script

echo "🚀 Starting NiveshakAI Web Application..."

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

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one with your OpenAI API key:"
    echo "   echo 'OPENAI_API_KEY=your_api_key_here' > .env"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/annual_reports
mkdir -p data/books
mkdir -p data/uploads
mkdir -p reports
mkdir -p logs

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

python app.py
