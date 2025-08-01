# NiveshakAI

> Your Personal AI Fundamental Investing Assistant

---

### This tool is under active development. Expect bugs, broken features etc. 

## Overview

**NiveshakAI** is a personal AI agent designed to help you become a smarter, data-driven fundamental investor.  
It reads and understands your chosen investing books, analyzes company annual reports, and provides buy/sell recommendations along with detailed explanations — all shaped by your personalized investor philosophy.

**🚀 Now featuring advanced OpenAI-powered analysis!** NiveshakAI leverages cutting-edge AI for intelligent financial analysis:

- **🤖 OpenAI GPT-4.1-nano**: Cost-efficient, high-performance model for intelligent PDF extraction and analysis
- **🧠 OpenAI Embeddings**: text-embedding-3-small (1536-dim) for superior knowledge retrieval
- **🏠 Local Fallback**: DeepSeek R1 7B via Ollama for offline operation when needed
- **📊 Multi-Year Trend Analysis**: Comprehensive 3-year financial data extraction
- **🔍 RAG-Powered Queries**: Retrieval-Augmented Generation with embedded investment knowledge

Optimized for performance, accuracy, and cost-effectiveness using OpenAI's latest models.

---

## Features

- 🤖 **OpenAI-Powered Analysis**: GPT-4.1-nano intelligently extracts financial data from annual reports
- 🧠 **Advanced RAG System**: OpenAI text-embedding-3-small (1536-dim) for superior knowledge retrieval
- 📚 **Investment Knowledge Base**: Process investing books with OpenAI embeddings for semantic search
- 📄 **Smart Annual Report Analysis**: AI-powered parsing of complex financial documents
- 🧠 **Personalized AI**: Embed your investor persona and risk profile for tailored recommendations
- 📊 **Comprehensive Valuations**: DCF, P/E ratio, and AI-enhanced fundamental analysis
- 🔄 **Hybrid Architecture**: OpenAI primary with local Ollama fallback for reliability
- 🛠️ **Flexible Configuration**: Optimized for performance and cost-effectiveness
- 📱 **CLI Interface**: Easy command-line interaction with future web UI planned
- ⚡ **Pre-loaded Content**: Ships with Philip Fisher's investment wisdom ready to query

---

## 🔧 Setup & Configuration

### 1. Basic Installation

```bash
# Clone repository
git clone <repository-url>
cd niveshak-ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure OpenAI API (Primary)

**NiveshakAI is optimized for OpenAI GPT-4.1-nano** for cost-effective, high-performance analysis:

1. **Get OpenAI API Key**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Configure API Key**: 
   ```bash
   cp .env.template .env
   # Edit .env file and add your key:
   # OPENAI_API_KEY=your-api-key-here
   ```

#### Optional: Local Fallback Setup

For offline capability when OpenAI is unavailable:

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai/)
2. **Pull Fallback Model**:
   ```bash
   ollama pull deepseek-r1:7b
   ```

### 3. Set Up Vector Database

**Qdrant** (recommended for OpenAI embeddings):
```bash
# Using Docker
docker run -d -p 6333:6333 qdrant/qdrant

# Or using Homebrew (macOS)
brew install qdrant/tap/qdrant
qdrant
```

### 4. Test Your Setup

```bash
# Test OpenAI integration
python main.py analyze ask --query "What are Philip Fisher's 15 points?"

# Test company analysis
python main.py analyze company --company ITC --query "Is ITC a good investment?"
```

---

## 📊 Stock Analysis Workflow

### Directory Structure for Annual Reports

Organize your annual reports using the following structure:

```
data/annual_reports/
├── ITC/
│   ├── 2023.pdf
│   ├── 2024.pdf
│   └── 2025.pdf
├── RELIANCE/
│   ├── 2023.pdf
│   ├── 2024.pdf
│   └── 2025.pdf
└── [OTHER_SYMBOLS]/
    ├── year.pdf
    └── ...
```

### Running AI-Powered Stock Analysis

1. **Prepare Annual Reports**: Place 3 years of annual reports in the appropriate directory structure
2. **Configure OpenAI API**: Set up your API key (see setup instructions above)
3. **Run Analysis**: The system will automatically use AI for intelligent data extraction
4. **Review Report**: Check the AI-generated analysis in the `reports/` folder

#### Example: ITC Analysis with AI

```bash
# Run ITC analysis with AI extraction
python fresh_itc_analysis.py

# AI will automatically:
# - Extract financial data from PDFs
# - Analyze business fundamentals
# - Generate comprehensive tables
# - Provide investment insights

# Report generated as: reports/ITC-2025-07-31.md
```

### OpenAI-Powered Analysis Features

- **🤖 Intelligent PDF Extraction**: GPT-4.1-nano reads and understands annual report content
- **📊 Automated Data Population**: Financial tables filled automatically by AI
- **📈 Multi-Year Trend Analysis**: 3-year CAGR calculations and growth patterns
- **🔍 Business Intelligence**: AI extracts qualitative business information
- **💡 Smart Insights**: OpenAI-powered interpretation of financial metrics
- **🧠 RAG Knowledge Retrieval**: text-embedding-3-small for precise knowledge matching
- **🛡️ Reliable Fallback**: Graceful degradation to local Ollama if OpenAI unavailable

### Generated AI Reports

Each AI analysis generates a comprehensive report including:

- **🏢 Company Profile**: AI-extracted business overview and fundamentals
- **💰 Financial Metrics**: Automatically populated financial data tables
- **📊 Ratio Analysis**: AI-calculated and interpreted financial ratios
- **🤖 AI Insights**: Intelligent analysis of business performance
- **📈 Trend Analysis**: Multi-year growth patterns and projections
- **💡 Investment Thesis**: AI-powered investment recommendations
- ~~OpenAI API key~~ **No longer needed!** - Runs completely offline

### Installation

#### Quick Setup (Recommended)

```bash
git clone https://github.com/<your-github-username>/niveshak-ai.git
cd niveshak-ai
./setup.sh
```

The setup script will:

- Create a Python virtual environment
- Install all dependencies
- Download and setup Ollama with required models
- Start local Qdrant vector database
- Generate configuration templates
- Set up directory structure

#### Manual Setup

1. **Install Ollama**:

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

2. **Download Required Models**:

```bash
# Large language model for analysis
ollama pull deepseek-r1:7b

# Embedding model for vector search
ollama pull nomic-embed-text
```

3. **Install NiveshakAI**:

```bash
git clone https://github.com/<your-github-username>/niveshak-ai.git
cd niveshak-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Qdrant vector database
docker run -p 6333:6333 qdrant/qdrant
```

4. **Verify Installation**:

```bash
# Test the complete RAG pipeline
python test_rag.py
```

- Make scripts executable

#### Manual Setup

```bash
git clone https://github.com/<your-github-username>/niveshak-ai.git
cd niveshak-ai
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### Configuration

1. **Edit API Keys**: Update `config/settings.yaml` with your API keys:

   ```yaml
   api_keys:
     openai_api_key: "your-actual-openai-key"
     alpha_vantage_key: "your-alpha-vantage-key"
   ```

2. **Customize Investment Persona**: Edit `config/persona.yaml` to match your investment style:
   ```yaml
   investor_profile:
     risk_tolerance: "moderate" # conservative, moderate, aggressive
     investment_horizon: "long_term"
     philosophy:
       style: "value_investing" # value_investing, growth_investing, dividend_investing
   ```

### Usage

## Quick Start

### 1. Test the Pre-loaded Knowledge Base

NiveshakAI comes with Philip Fisher's "Common Stocks and Uncommon Profits" already ingested! Try it immediately:

```bash
# Ask about Philip Fisher's investment principles
python -m src.cli.analyze ask --query "What are Philip Fisher's 15 points for stock analysis?"

# Learn about growth investing
python -m src.cli.analyze ask --query "How does Fisher identify quality growth companies?"

# Understand the scuttlebutt method
python -m src.cli.analyze ask --query "What is Fisher's scuttlebutt method for research?"
```

### 2. Add Your Own Investment Books

Place your investing books (PDF format) in `data/books/` and ingest them:

```bash
# Ingest a single book
python -m src.cli.ingest_books --file "data/books/your-investment-book.pdf"

# Ingest all books in the directory
python -m src.cli.ingest_books --directory "data/books/"
```

**Supported book examples**:

- Investment classics (Warren Buffett, Benjamin Graham, Peter Lynch)
- Financial analysis textbooks
- Sector-specific investment guides
- Any PDF finance/investing content

### 3. Company Analysis (Coming Soon)

```bash
# Analyze a specific company
python -m src.cli.analyze company --symbol AAPL --query "Is Apple a good long-term investment?"

# Compare multiple companies
python -m src.cli.analyze compare --symbols AAPL,MSFT,GOOGL
```

### 4. Demo Analysis

Run the Jupyter notebook for a complete demonstration:

```bash
jupyter notebook demo_analysis.ipynb
```

#### 3. Add Annual Reports

Place company annual reports in `data/annual_reports/` and process them:

```bash
python3 -m src.cli.ingest_reports --directory data/annual_reports/
```

#### 4. Analyze Companies

```bash
# Analyze a specific company
python3 -m src.cli.analyze --company RELIANCE --format structured

# Interactive analysis
python3 main.py --interactive
```

#### 5. Demo Analysis

Run the Jupyter notebook for a complete demonstration:

```bash
jupyter notebook demo_analysis.ipynb
```

## Knowledge Storage

NiveshakAI uses a modern local-first architecture:

### 1. **Vector Database** (Primary Knowledge Store)

- **Location**: Local Qdrant instance (`./data/qdrant_storage/`)
- **Dimensions**: 768 (Nomic embeddings)
- **Content**:
  - ✅ Philip Fisher's "Common Stocks and Uncommon Profits" (913 chunks)
  - 📚 Your additional finance books and investment content
  - 📄 Company annual reports (when added)
  - 🧠 Investment frameworks and analysis patterns

### 2. **Local AI Stack**

- **LLM**: DeepSeek R1 7B via Ollama (completely offline)
- **Embeddings**: Nomic-embed-text model (137M parameters)
- **Vector Search**: Qdrant for semantic similarity search
- **Privacy**: Zero data leaves your machine

### 3. **Raw Data Storage**

```text
data/
├── books/                    # Finance books (PDF, EPUB)
│   └── Common-Stocks-and-Uncommon-Profits.pdf  ✅ Pre-loaded
├── annual_reports/           # Company annual reports
├── qdrant_storage/          # Vector database files
└── embeddings/              # Cached embeddings (optional)
```

### 3. **Analysis Results**

- Excel exports: `niveshak_analysis.xlsx`
- CSV summaries: `niveshak_summary.csv`
- Structured JSON output for API integration

## Analysis Format

NiveshakAI provides structured analysis in 3 parts:

### 1. **Business & Qualitative Analysis**

- Company operations and business model
- Management background and track record
- Competitive position and moats
- Industry dynamics and regulatory environment

### 2. **Financial Metrics & Judgement**

- Revenue growth and profitability trends
- Cash flow analysis
- Debt levels and financial health
- Return ratios (ROE, ROA, ROCE)

### 3. **Ratio Analysis**

- Liquidity ratios (Current, Quick)
- Leverage ratios (Debt-to-Equity)
- Efficiency ratios (Asset turnover)
- Valuation ratios (P/E, P/B, P/S)

Each metric includes clear judgements: ✅ Good, ⚠️ Caution, ❌ Poor

## Investment Recommendations

Based on the analysis, NiveshakAI provides:

- **🎯 STRONG BUY** - Excellent fundamentals across metrics
- **👍 BUY** - Good fundamentals with some caution areas
- **⚖️ HOLD** - Mixed signals, monitor closely
- **🚫 AVOID** - Multiple red flags identified

## Example Analysis Output

```text
================================================================================
📊 NIVESHAKAI ANALYSIS: Investment Question Answered
================================================================================

🤔 QUESTION: What are Philip Fisher's key principles for growth investing?

🧠 AI ANALYSIS (Powered by DeepSeek R1 + Philip Fisher's Knowledge):
--------------------------------------------------
Based on Philip Fisher's "Common Stocks and Uncommon Profits," here are his key
principles for identifying exceptional growth companies:

🎯 THE 15 POINTS FOR STOCK ANALYSIS:
1. Sales Growth Potential - Look for companies with products/services that can
   significantly increase sales over years
2. Management Determination - Strong commitment to develop new products when
   current lines mature
3. R&D Effectiveness - Research efforts that translate into profitable products
4. Superior Sales Organization - Above-average marketing and distribution
5. Profit Margin Analysis - Worthwhile profit margins and improvement trends

[... Full detailed analysis continues ...]

📚 SOURCES FROM KNOWLEDGE BASE:
• Chapter 3: "What to Buy" - Common Stocks and Uncommon Profits
• Chapter 8: "The Investor and Market Fluctuations"
• Chapter 15: "A Different Type of Investment"

🎯 INVESTMENT WISDOM:
Fisher emphasizes quality over quantity - find exceptional companies and hold
them for the long term rather than frequent trading.
```

## Data Backup & Restore

🔒 **Protect Your Investment Knowledge Base**

NiveshakAI includes a comprehensive backup and restore system to protect your valuable data, including:

- Vector database with 913+ chunks of Philip Fisher's wisdom
- Your personal investment books and PDFs
- Configuration files and settings
- Embeddings cache and analysis history

### Quick Backup Commands

```bash
# Create a complete backup
./scripts/backup_data.sh

# List all available backups
./scripts/manage_backups.sh list

# Restore from the latest backup
./scripts/restore_data.sh latest

# Get detailed backup information
./scripts/manage_backups.sh info latest
```

### Backup Features

- **📦 Complete System Backup**: Vector databases, books, configs, and embeddings
- **🔍 Integrity Verification**: SHA256 checksums ensure data integrity
- **🗂️ Metadata Tracking**: JSON metadata with backup details and file counts
- **🧹 Automatic Cleanup**: Keeps last 5 backups automatically
- **⚡ Selective Restore**: Choose specific components to restore
- **🔒 Local Storage**: Backups stored in `~/niveshak-ai-backups/`

### Backup Management

```bash
# View backup storage usage
./scripts/manage_backups.sh size

# Verify backup integrity
./scripts/manage_backups.sh verify latest

# Delete old backups (keep last 3)
./scripts/manage_backups.sh cleanup 3

# Automated backup (for cron jobs)
./scripts/manage_backups.sh auto-backup
```

### Restore Options

```bash
# Full restore (replaces all data)
./scripts/restore_data.sh backup_20241201_143022.tar.gz

# Selective restore (choose components)
./scripts/restore_data.sh latest --selective

# Dry run (see what would be restored)
./scripts/restore_data.sh latest --dry-run

# Force restore (skip confirmations)
./scripts/restore_data.sh latest --force
```

### What Gets Backed Up

- **Vector Database**: Qdrant storage with all embeddings
- **Knowledge Base**: PDF books and investment materials
- **Configuration**: Settings, persona, and environment files
- **Embeddings Cache**: Pre-computed embeddings for faster access
- **Recent Logs**: Last 30 days of system logs

### Backup Best Practices

1. **Regular Backups**: Run weekly or after adding new books
2. **Before Updates**: Always backup before system updates
3. **Test Restores**: Periodically verify backup integrity
4. **External Storage**: Copy backups to external drives/cloud
5. **Document Changes**: Note what books/data you've added

### Example Backup Workflow

```bash
# 1. Check current data size
du -sh data/

# 2. Create backup before adding new books
./scripts/backup_data.sh

# 3. Add your new investment books
cp ~/Downloads/new-book.pdf data/books/
python -m src.cli.ingest_books --file "data/books/new-book.pdf"

# 4. Verify everything works
python test_rag.py

# 5. Create another backup with new data
./scripts/backup_data.sh

# 6. List your backups
./scripts/manage_backups.sh list
```

## Troubleshooting

### Common Issues

#### 1. **Ollama Connection Error**

```bash
# Check if Ollama is running
ollama list

# Start Ollama if not running
ollama serve

# Test with a simple query
ollama run deepseek-r1:7b "Hello, test message"
```

#### 2. **Missing Models**

```bash
# Download required models
ollama pull deepseek-r1:7b
ollama pull nomic-embed-text

# Verify models are available
ollama list
```

#### 3. **Qdrant Database Issues**

```bash
# Start Qdrant locally
docker run -p 6333:6333 qdrant/qdrant

# Check if Qdrant is running
curl http://localhost:6333
```

#### 4. **PDF Processing Errors**

```bash
# Install additional dependencies if needed
pip install PyMuPDF

# Test PDF integrity
python -c "
import fitz
doc = fitz.open('data/books/your_book.pdf')
print(f'Pages: {doc.page_count}')
"
```

#### 5. **Memory Issues with Large Models**

- Use smaller models: `ollama pull llama3.2:3b` instead of DeepSeek R1
- Adjust chunk size in `config/settings.yaml`
- Process books one at a time
- Monitor system resources

### Performance Tips

1. **Test Pipeline**: Use `python test_rag.py` to verify everything works
2. **Model Selection**: DeepSeek R1 7B for quality, Llama 3.2 3B for speed
3. **Batch Processing**: Ingest multiple books efficiently
4. **Local Storage**: Keep vector database on SSD for faster search

## Roadmap

### Short Term (Q2 2025)

- [ ] Web UI interface
- [ ] Real-time data integration
- [ ] Portfolio tracking
- [ ] Advanced screening filters

### Medium Term (Q3-Q4 2025)

- [ ] Multi-language support
- [ ] Mobile app
- [ ] Automated report generation
- [ ] Social sentiment analysis

### Long Term (2026+)

- [ ] Options analysis
- [ ] Crypto asset analysis
- [ ] Global market expansion
- [ ] Institutional features

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for:

- Development setup instructions
- Architecture deep-dive
- PDF ingestion pipeline details
- Knowledge storage system
- Adding new features
- Testing guidelines
- Code style requirements

### Quick Start for Contributors

```bash
# Fork the repo and clone
git clone https://github.com/your-username/niveshak-ai.git
cd niveshak-ai

# Setup development environment
./setup.sh
source venv/bin/activate

# Run tests
python -m pytest tests/ -v

# Start contributing!
```

## License

This project is licensed under the Apache-2.0 license - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Benjamin Graham** - For the foundational principles of value investing
- **Warren Buffett** - For practical wisdom in fundamental analysis
- **Open Source Community** - For the amazing tools and libraries
- **Contributors** - Everyone who helps make NiveshakAI better

## Support

- 📧 **Issues**: [GitHub Issues](https://github.com/sanusatyadarshi/niveshak-ai/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/sanusatyadarshi/niveshak-ai/discussions)
- 📖 **Documentation**: See `demo_analysis.ipynb` for detailed examples
- 🤝 **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**⚠️ Disclaimer**: NiveshakAI is a research and educational tool. All investment decisions should be made after proper due diligence and consultation with qualified financial advisors. Past performance does not guarantee future results.

**🤖 Made with ❤️  and LLM by @sanusatyadarshi**
