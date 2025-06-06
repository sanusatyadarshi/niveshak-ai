#!/bin/bash

# NiveshakAI Local RAG Setup Script
# Sets up complete local AI infrastructure with Ollama + Qdrant + Philip Fisher knowledge

set -e

echo "🚀 NiveshakAI Local RAG Setup"
echo "============================="
echo "Setting up complete local AI infrastructure..."
echo ""

# Check Python version
echo "📍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10+ is required. Found: $python_version"
    exit 1
fi
echo "✅ Python version: $python_version"

# Check if Ollama is installed
echo "📍 Checking Ollama installation..."
if command -v ollama &>/dev/null; then
    echo "✅ Ollama is installed"
else
    echo "❌ Ollama not found. Installing Ollama..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &>/dev/null; then
            brew install ollama
        else
            echo "Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    else
        # Linux
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
    echo "✅ Ollama installed"
fi

# Check if Docker is installed
echo "📍 Checking Docker installation..."
if command -v docker &>/dev/null; then
    echo "✅ Docker is installed"
else
    echo "❌ Docker not found. Please install Docker: https://docker.com/get-started"
    exit 1
fi

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
echo "📍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Create configuration files from templates
echo "📍 Setting up configuration..."

# Create settings.yaml if it doesn't exist
if [ ! -f "config/settings.yaml" ]; then
    cat >config/settings.yaml <<EOF
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
  provider: "ollama"  # Options: openai, ollama
  model: "nomic-embed-text"  # For Ollama: nomic-embed-text, For OpenAI: text-embedding-3-small
  chunk_size: 1000
  chunk_overlap: 200

# LLM Configuration
llm:
  provider: "ollama"  # Options: openai, ollama
  model: "deepseek-r1:7b"  # For Ollama: deepseek-r1:7b, llama3.2:3b
  temperature: 0.1
  max_tokens: 1000

# Local AI Configuration (Ollama)
ollama:
  base_url: "http://localhost:11434"
  models:
    embedding: "nomic-embed-text"
    chat: "deepseek-r1:7b"

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
    cat >config/persona.yaml <<EOF
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

# Start Ollama service
echo "📍 Starting Ollama service..."
if pgrep -x "ollama" >/dev/null; then
    echo "✅ Ollama service is already running"
else
    echo "Starting Ollama service..."
    ollama serve &
    sleep 3
    echo "✅ Ollama service started"
fi

# Download required models
echo "📍 Downloading AI models..."
echo "This may take several minutes for the first time..."

# Download embedding model
echo "Downloading Nomic embedding model..."
ollama pull nomic-embed-text
echo "✅ Nomic embedding model ready"

# Download LLM model (DeepSeek R1 7B)
echo "Downloading DeepSeek R1 7B model..."
ollama pull deepseek-r1:7b
echo "✅ DeepSeek R1 7B model ready"

# Start Qdrant vector database
echo "📍 Starting Qdrant vector database..."
if docker ps | grep -q qdrant; then
    echo "✅ Qdrant is already running"
else
    docker run -d -p 6333:6333 -v $(pwd)/data/qdrant_storage:/qdrant/storage qdrant/qdrant
    sleep 5
    echo "✅ Qdrant vector database started"
fi

# Test the installation
echo "📍 Testing installation..."
if python3 test_rag.py; then
    echo "✅ Installation test passed"
else
    echo "⚠️ Installation test failed - check the output above"
fi

echo ""
echo "🎉 NiveshakAI Local RAG Setup Complete!"
echo "========================================="
echo ""
echo "✅ Local AI Infrastructure Ready:"
echo "   • DeepSeek R1 7B (Chat LLM)"
echo "   • Nomic-embed-text (Embeddings)"
echo "   • Qdrant Vector Database"
echo "   • Philip Fisher knowledge pre-loaded"
echo ""
echo "🚀 Quick Start:"
echo "1. Test the system: python3 test_rag.py"
echo "2. Ask investment questions: python3 -m src.cli.analyze --query \"What are Fisher's 15 points?\""
echo "3. Add more books: python3 -m src.cli.ingest_books --file data/books/your_book.pdf"
echo "4. Demo analysis: jupyter notebook demo_analysis.ipynb"
echo ""
echo "📁 Important directories:"
echo "   • data/books/ - Add PDF investment books here"
echo "   • config/ - Customize your investment persona"
echo "   • logs/ - View system logs"
echo ""
echo "🔧 Configuration:"
echo "   • Edit config/persona.yaml for your investment style"
echo "   • API keys in .env (optional, for backup OpenAI access)"
echo ""
echo "📖 For more information, see README.md and CONTRIBUTING.md"
