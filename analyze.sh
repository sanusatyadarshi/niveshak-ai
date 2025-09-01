#!/bin/bash

# 🚀 NiveshakAI One-Command Analyzer
# Quick analysis launcher for companies with pre-loaded annual reports

set -e

echo "🚀 NiveshakAI Quick Analyzer"
echo "============================"

# Default company if none provided
COMPANY=${1:-ITC}
QUERY=${2:-"Complete fundamental analysis"}

echo "📊 Analyzing: $COMPANY"
echo "🔍 Query: $QUERY"
echo ""

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if dependencies are installed
python -c "import yaml" 2>/dev/null || {
    echo "📦 Installing missing dependencies..."
    pip install -r requirements.txt
}

# Create required directories
mkdir -p data/annual_reports/$COMPANY
mkdir -p reports
mkdir -p logs

# Check if annual reports exist for the company
if [ ! "$(ls -A data/annual_reports/$COMPANY 2>/dev/null)" ]; then
    echo "⚠️  No annual reports found for $COMPANY"
    echo "📁 Please add PDF files to: data/annual_reports/$COMPANY/"
    echo "   Expected files: 2023.pdf, 2024.pdf, 2025.pdf"
    echo ""
    echo "📋 Available companies with reports:"
    ls -1 data/annual_reports/ 2>/dev/null | grep -v README.md || echo "   None found"
    exit 1
fi

echo "✅ Found annual reports for $COMPANY:"
ls -1 data/annual_reports/$COMPANY/

echo ""
echo "🤖 Starting AI analysis..."
echo "================================"

# Run the analysis
python main.py analyze company --company "$COMPANY" --query "$QUERY"

echo ""
echo "✅ Analysis complete!"
echo "📄 Report saved to: reports/$COMPANY-$(date +%Y-%m-%d).md"
echo ""
echo "🎯 Quick commands for other analyses:"
echo "   ./analyze.sh RELIANCE"
echo "   ./analyze.sh TCS \"Growth analysis\""
echo "   ./analyze.sh HDFC \"Dividend analysis\""
