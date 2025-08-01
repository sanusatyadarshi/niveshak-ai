# 🚀 Simplified Setup Guide - Niveshak AI

## Prerequisites

- Python 3.8+ installed
- macOS (you're already on macOS)
- Terminal access

---

## Step 1: Clone and Navigate

```bash
cd ~/Documents/repos/personal
git clone <your-repo> niveshak-ai
cd niveshak-ai
```

## Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Set Up API Keys (Choose One Option)

### Option A: OpenAI API (Recommended for Best Results)

1. Get OpenAI API key from: https://platform.openai.com/api-keys
2. Create `.env` file:

```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### Option B: Local AI (Free, but requires setup)

1. Install Ollama: https://ollama.ai/download
2. Pull the models:

```bash
ollama pull deepseek-r1:7b
ollama pull nomic-embed-text
```

## Step 5: Set Up Vector Database (Choose One)

### Option A: Qdrant (Recommended)

```bash
# Install Qdrant
brew install qdrant/tap/qdrant
# Start Qdrant
qdrant
```

### Option B: Weaviate (Alternative)

```bash
# Using Docker
docker run -d -p 8080:8080 semitechnologies/weaviate:latest
```

## Step 6: Create Data Directories

```bash
mkdir -p data/annual_reports/ITC
mkdir -p data/books
mkdir -p reports
mkdir -p logs
```

## Step 7: Add Sample Annual Report (Optional)

- Download ITC's annual report (2023.pdf, 2024.pdf)
- Place in: `data/annual_reports/ITC/`

---

## 🎯 Quick Test

### Test 1: Basic Setup

```bash
python main.py --help
```

### Test 2: Company Analysis

```bash
python main.py analyze company --company ITC --query "Complete fundamental analysis"
```

### Test 3: Check Generated Report

```bash
ls -la reports/
```

---

## 🔧 Configuration

### For OpenAI Users:

- Edit `config/settings.yaml`
- Set `llm.provider: openai`
- Set `pdf_analysis.provider: openai`

### For Local AI Users:

- Edit `config/settings.yaml`
- Set `llm.provider: ollama`
- Set `pdf_analysis.provider: ollama`

---

## 📁 Directory Structure After Setup

```
niveshak-ai/
├── venv/                    # Virtual environment
├── data/
│   ├── annual_reports/
│   │   └── ITC/
│   │       ├── 2023.pdf
│   │       └── 2024.pdf
│   └── books/               # Investment books
├── reports/                 # Generated analysis reports
├── logs/                    # Application logs
├── .env                     # API keys
└── config/settings.yaml     # Configuration
```

---

## ⚡ Quick Commands

### Daily Usage:

```bash
# Activate environment
source venv/bin/activate

# Analyze a company
python main.py analyze company --company RELIANCE --query "Is it a good buy?"

# Ask investment questions
python main.py analyze ask --query "What are the best value stocks in India?"

# Compare companies
python main.py analyze compare --companies TCS,INFY,WIPRO
```

### Add Investment Books:

```bash
python main.py ingest books --directory data/books
```

### Add Annual Reports:

```bash
python main.py ingest reports --file data/annual_reports/RELIANCE/2024.pdf --company RELIANCE --year 2024
```

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'yaml'`

**Solution:**

```bash
source venv/bin/activate
pip install pyyaml
```

### Issue: `Error: cannot import name 'DCFAnalyzer' from 'src.analysis.valuation'`

**Solution:** ✅ **FIXED** - The valuation module has been updated with all required classes.

### Issue: Qdrant connection failed

**Solution:**

```bash
# Check if Qdrant is running
curl http://localhost:6333/health
# If not, start it:
qdrant
```

### Issue: OpenAI API errors

**Solution:**

```bash
# Check your .env file
cat .env
# Verify API key is valid at platform.openai.com
```

### Issue: Permission denied

**Solution:**

```bash
chmod +x main.py
```

---

## 🎯 What You'll Get

After setup, you can:

- ✅ Analyze any Indian stock (NSE/BSE)
- ✅ Get AI-powered fundamental analysis reports
- ✅ DCF valuation with buy/sell recommendations
- ✅ Template-based comprehensive analysis
- ✅ Multi-year trend analysis
- ✅ Risk assessment and investment recommendations

## 📊 Example Output

Running the analysis will generate reports like:

- `reports/ITC-2025-08-01.md` - Complete fundamental analysis
- Includes 18 company questions, 10 financial metrics, 11 ratios
- DCF valuation with intrinsic value calculation
- Buy/Hold/Sell recommendation with confidence level

---

## 🚀 Ready to Start!

Your Niveshak AI is now ready. Start with:

```bash
source venv/bin/activate
python main.py analyze company --company ITC --query "Complete analysis"
```

Happy investing! 📈
