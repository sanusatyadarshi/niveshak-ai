#!/bin/bash

# Quick setup script for NiveshakAI
# This script sets up the development environment and basic configuration

set -e

echo "🤖 NiveshakAI Quick Setup"
echo "========================="

# Check Python version
echo "📍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10+ is required. Found: $python_version"
    exit 1
fi
echo "✅ Python version: $python_version"

# Create virtual environment
echo "📍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "📍 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📍 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create configuration files from templates
echo "📍 Setting up configuration..."

# Create settings.yaml if it doesn't exist
if [ ! -f "config/settings.yaml" ]; then
    cat > config/settings.yaml << EOF
# NiveshakAI Configuration
app:
  name: "NiveshakAI"
  version: "1.0.0"
  debug: false

# API Keys (Set these with your actual keys)
api_keys:
  openai_api_key: "your-openai-api-key-here"
  alpha_vantage_key: "your-alpha-vantage-key-here"
  finnhub_key: "your-finnhub-key-here"

# Vector Database Configuration
vector_db:
  provider: "qdrant"  # Options: qdrant, weaviate
  host: "localhost"
  port: 6333
  collection_name: "niveshak_embeddings"
  
# Embedding Configuration
embeddings:
  provider: "openai"
  model: "text-embedding-3-small"
  chunk_size: 1000
  chunk_overlap: 200

# Analysis Configuration
analysis:
  default_risk_free_rate: 0.03
  default_market_return: 0.10
  dcf_years: 5
  
# Logging
logging:
  level: "INFO"
  file: "logs/niveshak.log"
  max_size_mb: 10
  backup_count: 5
EOF
    echo "✅ Created config/settings.yaml"
else
    echo "✅ config/settings.yaml already exists"
fi

# Create persona.yaml if it doesn't exist
if [ ! -f "config/persona.yaml" ]; then
    cat > config/persona.yaml << EOF
# Investor Persona Configuration
investor_profile:
  name: "Default Investor"
  risk_tolerance: "moderate"  # Options: conservative, moderate, aggressive
  investment_horizon: "long_term"  # Options: short_term, medium_term, long_term
  
  # Investment Philosophy
  philosophy:
    style: "value_investing"  # Options: value_investing, growth_investing, dividend_investing
    preferred_sectors: ["technology", "healthcare", "consumer_goods"]
    avoid_sectors: ["tobacco", "gambling"]
    
  # Financial Criteria
  criteria:
    min_market_cap: 1000000000  # $1B minimum
    max_debt_to_equity: 0.5
    min_roe: 0.15  # 15%
    min_current_ratio: 1.2
    
  # Qualitative Preferences
  preferences:
    management_quality_weight: 0.3
    competitive_moat_weight: 0.4
    financial_strength_weight: 0.3
    
  # Custom Rules
  custom_rules:
    - "Avoid companies with declining revenue for 2+ years"
    - "Prefer companies with consistent dividend payments"
    - "Focus on companies with strong brand recognition"
EOF
    echo "✅ Created config/persona.yaml"
else
    echo "✅ config/persona.yaml already exists"
fi

# Create logs directory
mkdir -p logs
echo "✅ Created logs directory"

# Make scripts executable
chmod +x scripts/*.sh
echo "✅ Made scripts executable"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config/settings.yaml to add your API keys"
echo "2. Customize config/persona.yaml to match your investment style"
echo "3. Start a vector database: ./scripts/run_local_vector_db.sh start"
echo "4. Test the installation: python3 main.py --help"
echo ""
echo "For more information, see README.md"
