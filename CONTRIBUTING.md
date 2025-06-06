# Contributing to NiveshakAI

Welcome! We're excited that you want to contribute to NiveshakAI. This guide will help you get started with development, understanding the architecture, and making meaningful contributions.

## Table of Contents

- [Development Setup](#development-setup)
- [Architecture Overview](#architecture-overview)
- [Knowledge Storage System](#knowledge-storage-system)
- [PDF Book Ingestion](#pdf-book-ingestion)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submission Guidelines](#submission-guidelines)

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- Docker (for vector database)
- OpenAI API key

### Quick Start

1. **Clone and Setup**

   ```bash
   git clone https://github.com/<your-github-username>/niveshak-ai.git
   cd niveshak-ai
   ./setup.sh
   ```

2. **Activate Virtual Environment**

   ```bash
   source venv/bin/activate
   ```

3. **Configure API Keys**
   Edit `config/settings.yaml`:

   ```yaml
   api_keys:
     openai_api_key: "your-openai-api-key"
     alpha_vantage_key: "your-alpha-vantage-key"
   ```

4. **Start Vector Database**

   ```bash
   ./scripts/run_local_vector_db.sh start
   ```

5. **Run Tests**
   ```bash
   python -m pytest tests/ -v
   ```

## Architecture Overview

### Core Components

```
src/
├── ingestion/              # Data ingestion modules
│   ├── books.py           # PDF book processing
│   ├── reports.py         # Annual report processing
│   └── __init__.py
├── embedding/             # Vector database management
│   ├── embedder.py        # Embedding creation & storage
│   └── __init__.py
├── analysis/              # AI analysis engines
│   ├── query.py           # RAG-based analysis
│   ├── valuation.py       # Financial valuation models
│   └── __init__.py
├── cli/                   # Command-line interface
│   ├── ingest_books.py    # Book ingestion CLI
│   ├── ingest_reports.py  # Report ingestion CLI
│   ├── analyze.py         # Analysis CLI
│   └── __init__.py
└── utils/                 # Utility modules
    ├── pdf_utils.py       # PDF processing utilities
    ├── financial_utils.py # Financial calculations
    ├── logger.py          # Logging configuration
    └── __init__.py
```

### Data Flow

1. **Ingestion**: PDFs → Text chunks → Embeddings → Vector DB
2. **Analysis**: Query → RAG retrieval → LLM analysis → Structured output
3. **Output**: JSON/Excel/CSV → Investment recommendations

## Knowledge Storage System

### Vector Database Architecture

NiveshakAI uses a multi-layered knowledge storage system:

#### 1. Vector Database (Primary)

- **Technology**: Qdrant (default) or Weaviate
- **Location**: `./data/qdrant_storage/`
- **Content**: Embedded text chunks from books and reports
- **Configuration**: `config/settings.yaml`

```yaml
vector_db:
  provider: "qdrant"
  host: "localhost"
  port: 6333
  collection_name: "niveshak_embeddings"
```

#### 2. Raw Data Storage

```
data/
├── books/                    # Finance books (PDF, EPUB)
│   ├── warren_buffett_letters.pdf
│   ├── intelligent_investor.pdf
│   └── security_analysis.pdf
├── annual_reports/           # Company annual reports
│   ├── RELIANCE_AR_2024.pdf
│   ├── TCS_AR_2024.pdf
│   └── HDFC_BANK_AR_2024.pdf
├── qdrant_storage/          # Vector database persistence
│   ├── collection/
│   └── meta.json
└── embeddings/              # Cached embeddings
    └── cache/
```

#### 3. Analysis Results Cache

- **Location**: Generated in project root
- **Formats**: Excel, CSV, JSON
- **Examples**: `niveshak_analysis.xlsx`, `niveshak_summary.csv`

### Embedding Process

```python
# Example from src/embedding/embedder.py
class EmbeddingManager:
    def store_embeddings(self, texts: List[str], metadata: List[Dict]):
        """Store text chunks as embeddings in vector database"""
        embeddings = self.embedding_model.embed_documents(texts)
        return self.vector_db.add_vectors(embeddings, metadata)
```

## PDF Book Ingestion

### Supported Formats

- **PDF**: Primary format for books and reports
- **EPUB**: Supported for e-books
- **Text**: Plain text files

### Ingestion Pipeline

#### 1. **Text Extraction** (`src/utils/pdf_utils.py`)

```python
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF files"""
    # Uses PyMuPDF for high-quality text extraction
    # Handles complex layouts, tables, and figures
```

#### 2. **Text Chunking** (`src/ingestion/books.py`)

```python
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for embedding"""
    # Preserves context across chunk boundaries
    # Optimized for finance content structure
```

#### 3. **Metadata Extraction**

```python
def extract_metadata(file_path: str) -> Dict[str, Any]:
    """Extract book metadata (title, author, year, etc.)"""
    return {
        "title": "The Intelligent Investor",
        "author": "Benjamin Graham",
        "file_path": file_path,
        "chapter": "Chapter 1",
        "page_range": "1-25"
    }
```

#### 4. **Embedding Creation**

```python
def create_embeddings(chunks: List[str]) -> List[List[float]]:
    """Convert text chunks to vector embeddings"""
    # Uses OpenAI text-embedding-3-small by default
    # Configurable in settings.yaml
```

### Adding New Books

1. **Place PDF in Directory**

   ```bash
   cp your_finance_book.pdf data/books/
   ```

2. **Run Ingestion**

   ```bash
   python3 -m src.cli.ingest_books --directory data/books/
   ```

3. **Verify Ingestion**
   ```bash
   # Check vector database
   python3 -c "
   from src.embedding.embedder import EmbeddingManager
   em = EmbeddingManager()
   print(f'Total vectors: {em.get_collection_info()}')
   "
   ```

### Book Recommendations for Training

#### Classic Investment Books

- **The Intelligent Investor** - Benjamin Graham
- **Security Analysis** - Benjamin Graham & David Dodd
- **Warren Buffett Letters** - Warren Buffett
- **One Up On Wall Street** - Peter Lynch
- **Common Stocks and Uncommon Profits** - Philip Fisher

#### Financial Analysis Books

- **Financial Statement Analysis** - Martin Fridson
- **Valuation: Measuring and Managing** - McKinsey & Company
- **The Little Book of Valuation** - Aswath Damodaran

#### Sector-Specific Guides

- **Technology investing guides**
- **Healthcare sector analysis**
- **Real estate investment books**

## Adding New Features

### 1. Analysis Modules

To add a new analysis method (e.g., momentum analysis):

```python
# src/analysis/momentum.py
class MomentumAnalyzer:
    def __init__(self, config):
        self.config = config

    def analyze_price_momentum(self, symbol: str) -> Dict[str, Any]:
        """Analyze price momentum indicators"""
        return {
            "rsi": self.calculate_rsi(symbol),
            "moving_averages": self.calculate_ma(symbol),
            "momentum_score": self.calculate_momentum_score(symbol)
        }
```

### 2. New Data Sources

To add support for new financial data APIs:

```python
# src/ingestion/new_source.py
class NewDataSource:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_company_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data from new API source"""
        pass
```

### 3. CLI Commands

Add new CLI commands in `src/cli/`:

```python
# src/cli/new_command.py
import argparse
from src.analysis.momentum import MomentumAnalyzer

def main():
    parser = argparse.ArgumentParser(description='New analysis command')
    parser.add_argument('--symbol', required=True, help='Company symbol')
    args = parser.parse_args()

    analyzer = MomentumAnalyzer()
    result = analyzer.analyze_price_momentum(args.symbol)
    print(result)

if __name__ == '__main__':
    main()
```

## Testing

### Test Structure

```
tests/
├── test_ingestion/         # Ingestion module tests
├── test_embedding/         # Embedding tests
├── test_analysis/          # Analysis engine tests
├── test_cli/              # CLI command tests
└── test_utils/            # Utility function tests
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_analysis/test_valuation.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Writing Tests

```python
# Example test: tests/test_analysis/test_valuation.py
import pytest
from src.analysis.valuation import ValuationAnalyzer

class TestValuationAnalyzer:
    def setup_method(self):
        self.analyzer = ValuationAnalyzer({})

    def test_dcf_calculation(self):
        financials = {
            "free_cash_flow": 1000000,
            "growth_rate": 0.05,
            "discount_rate": 0.10
        }

        dcf_value = self.analyzer.calculate_dcf(financials)
        assert dcf_value > 0
        assert isinstance(dcf_value, float)
```

## Code Style

### Python Style Guide

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for all functions and classes

### Example Function

```python
def analyze_financial_metrics(
    self,
    company_symbol: str,
    financials: Dict[str, float]
) -> Dict[str, Dict[str, Any]]:
    """
    Analyze financial metrics and provide judgements.

    Args:
        company_symbol: Stock symbol (e.g., 'RELIANCE')
        financials: Dictionary of financial data

    Returns:
        Dictionary with metrics and judgements

    Example:
        >>> analyzer = NiveshakAIAnalyzer(config)
        >>> result = analyzer.analyze_financial_metrics('RELIANCE', data)
        >>> print(result['roe']['judgement'])
        '✅ Excellent'
    """
    # Implementation here
    pass
```

### Configuration Style

```yaml
# config/settings.yaml - Use clear, hierarchical structure
app:
  name: "NiveshakAI"
  version: "1.0.0"

api_keys:
  openai_api_key: "your-key-here"

vector_db:
  provider: "qdrant"
  host: "localhost"
  port: 6333
```

## Submission Guidelines

### Before Submitting

1. **Run Tests**: Ensure all tests pass

   ```bash
   python -m pytest tests/ -v
   ```

2. **Check Code Style**: Use flake8 or black

   ```bash
   flake8 src/
   black src/ --check
   ```

3. **Update Documentation**: Add docstrings and update README if needed

4. **Test Integration**: Run the demo notebook to ensure everything works

### Pull Request Process

1. **Fork the Repository**
2. **Create Feature Branch**

   ```bash
   git checkout -b feature/momentum-analysis
   ```

3. **Make Changes and Test**
4. **Commit with Clear Messages**

   ```bash
   git commit -m "feat: add momentum analysis module

   - Implement RSI calculation
   - Add moving average analysis
   - Include momentum scoring system
   - Add comprehensive tests"
   ```

5. **Push and Create PR**

   ```bash
   git push origin feature/momentum-analysis
   ```

6. **PR Description Template**

   ```markdown
   ## Description

   Brief description of changes

   ## Type of Change

   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing

   - [ ] Tests pass locally
   - [ ] Added new tests for new functionality
   - [ ] Manual testing completed

   ## Checklist

   - [ ] Code follows project style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   ```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Examples**:

- `feat(analysis): add momentum analysis module`
- `fix(ingestion): handle PDF parsing errors gracefully`
- `docs(readme): update installation instructions`

## Getting Help

- **Issues**: Check existing issues or create new ones
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Refer to docstrings and demo notebook
- **Contact**: Open an issue for any clarification needed

Thank you for contributing to NiveshakAI! 🚀
