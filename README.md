# NiveshakAI

> Your Personal AI Fundamental Investing Assistant

---

## Overview

**NiveshakAI** is a personal AI agent designed to help you become a smarter, data-driven fundamental investor.  
It reads and understands your chosen investing books, analyzes company annual reports, and provides buy/sell recommendations along with detailed explanations — all shaped by your personalized investor philosophy.

Inspired by classic investing wisdom and powered by modern LLMs and vector search, NiveshakAI is your intelligent investing companion.

---

## Features

- 📚 Ingest investing books from any market (e.g. Warrent Buffet, Philip Fisher)
- 📄 Parse and analyze company annual reports from multiple markets
- 🧠 Embed your investor persona and risk profile for tailored recommendations
- 📊 Perform fundamental valuations like Discounted Cash Flow (DCF) and P/E ratio
- 🤖 Answer your queries with transparent explanations and data-backed reasoning
- 🛠️ CLI interface for easy interaction, with future plans for web UI

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` package manager
- [Qdrant](https://qdrant.tech/) or [Weaviate](https://weaviate.io/) vector database running locally or remotely
- OpenAI API key or compatible LLM provider

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
- Generate configuration templates
- Set up directory structure
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

#### 1. Start Vector Database

```bash
./scripts/run_local_vector_db.sh start
```

#### 2. Ingest Finance Books (PDF Format)

Place your finance books in the `data/books/` directory and run:

```bash
python3 -m src.cli.ingest_books --directory data/books/
```

**Supported Books:**

- Investment classics (Warren Buffett, Benjamin Graham, Peter Lynch)
- Financial analysis textbooks
- Sector-specific investment guides
- Any PDF finance/investing content

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

NiveshakAI stores knowledge in multiple layers:

### 1. **Vector Database** (Primary Knowledge Store)

- **Location**: Local Qdrant instance (`./data/qdrant_storage/`)
- **Content**:
  - Embedded finance book chapters
  - Annual report sections
  - Company analysis chunks
  - Investment frameworks

### 2. **Raw Data Storage**

```
data/
├── books/                    # Finance books (PDF, EPUB)
├── annual_reports/           # Company annual reports
├── qdrant_storage/          # Vector database files
└── embeddings/              # Cached embeddings
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

```
================================================================================
📊 NIVESHAKAI ANALYSIS: Trent Limited (TRENT)
================================================================================

🏢 SECTION 1: BUSINESS & QUALITATIVE ANALYSIS
--------------------------------------------------
• What Does Company Do: Trent Limited operates in the Retail sector with strong market presence
• Promoters Background: Experienced management team with strong track record
• Competitors: Major players in Retail include established market leaders
• Revenue Mix: Diversified revenue streams within Retail
• Entry Barriers: High barriers due to capital requirements and regulatory compliance

💰 SECTION 2: FINANCIAL METRICS & JUDGEMENT
--------------------------------------------------
• Gross Profit Margin: 40.0% | ✅ Strong
• Roe: 24.9% | ✅ Excellent
• Debt Level: 0.19 | ✅ Low
• Cash Flow Operations: 21.8% | ✅ Strong

📈 SECTION 3: RATIO ANALYSIS
--------------------------------------------------
• Current Ratio: 1.50 | ✅ Healthy
• Quick Ratio: 1.05 | ✅ Good
• Roe: 24.9% | ✅ Excellent
• Roa: 10.3% | ✅ Strong
• Debt Equity: 0.19 | ✅ Conservative

🎯 INVESTMENT RECOMMENDATION
--------------------------------------------------
Decision: 🎯 STRONG BUY - Excellent fundamentals across multiple metrics
Confidence: High
Summary: Analysis shows 7 positive, 1 neutral, and 0 negative indicators
```

## Troubleshooting

### Common Issues

#### 1. **Vector Database Connection Error**

```bash
# Check if Qdrant is running
./scripts/run_local_vector_db.sh status

# Restart if needed
./scripts/run_local_vector_db.sh restart
```

#### 2. **PDF Processing Errors**

```bash
# Install additional dependencies
pip install PyMuPDF fitz

# Check PDF file integrity
python3 -c "
import fitz
doc = fitz.open('data/books/your_book.pdf')
print(f'Pages: {doc.page_count}')
"
```

#### 3. **OpenAI API Rate Limits**

- Check your API usage in OpenAI dashboard
- Consider using smaller embedding models
- Implement retry logic with exponential backoff

#### 4. **Memory Issues with Large PDFs**

- Increase chunk size in `config/settings.yaml`
- Process books one at a time
- Use smaller embedding models

### Performance Tips

1. **Optimize Chunk Size**: Adjust based on your content type
2. **Batch Processing**: Process multiple files in batches
3. **Caching**: Enable embedding caching for repeated analysis
4. **Resource Monitoring**: Monitor RAM and disk usage

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Benjamin Graham** - For the foundational principles of value investing
- **Warren Buffett** - For practical wisdom in fundamental analysis
- **Open Source Community** - For the amazing tools and libraries
- **Contributors** - Everyone who helps make NiveshakAI better

## Support

- 📧 **Issues**: [GitHub Issues](https://github.com/your-username/niveshak-ai/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/niveshak-ai/discussions)
- 📖 **Documentation**: See `demo_analysis.ipynb` for detailed examples
- 🤝 **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**⚠️ Disclaimer**: NiveshakAI is a research and educational tool. All investment decisions should be made after proper due diligence and consultation with qualified financial advisors. Past performance does not guarantee future results.

**🤖 Made with ❤️ by the NiveshakAI team**
