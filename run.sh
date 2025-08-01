#!/bin/bash

# 🚀 Niveshak AI Quick Start Script
# This script helps you run Niveshak AI with minimal setup

echo "🚀 Starting Niveshak AI..."
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if required dependencies are installed
python -c "import yaml" 2>/dev/null || {
    echo "📦 Installing missing dependencies..."
    pip install pyyaml
}

# Check for API keys
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat >.env <<EOF
# Add your API keys here
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FMP_API_KEY=your_fmp_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
EOF
    echo "📝 Please edit .env file with your API keys"
else
    # Check if OpenAI API key is configured
    if grep -q "^OPENAI_API_KEY=sk-" .env; then
        echo "✅ OpenAI API key found - AI analysis enabled"
    else
        echo "⚠️  OpenAI API key not found. Add your key to .env file for AI analysis"
        echo "   Get your key from: https://platform.openai.com/api-keys"
    fi
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p data/annual_reports/ITC
mkdir -p data/books
mkdir -p reports
mkdir -p logs

# Check if Qdrant is running (optional)
curl -s http://localhost:6333/health >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Qdrant vector database is running"
else
    echo "⚠️  Qdrant not running. Vector search features may be limited."
    echo "   To install: brew install qdrant/tap/qdrant"
    echo "   To start: qdrant"
fi

echo ""
echo "🎯 Quick Commands:"
echo "================================"
echo "1. Company Analysis:"
echo "   python main.py analyze company --company ITC --query \"Complete analysis\""
echo ""
echo "2. Ask Investment Questions:"
echo "   python main.py analyze ask --query \"What are good value stocks?\""
echo ""
echo "3. Compare Companies:"
echo "   python main.py analyze compare --companies TCS,INFY,WIPRO"
echo ""
echo "4. View Help:"
echo "   python main.py --help"
echo ""

# If no arguments provided, show help
if [ $# -eq 0 ]; then
    echo "💡 No command provided. Showing help..."
    python main.py --help
else
    # Run the provided command
    echo "🚀 Running: python main.py $@"
    python main.py "$@"
fi

echo ""
echo "✅ Done! Check the 'reports/' directory for generated analysis."
