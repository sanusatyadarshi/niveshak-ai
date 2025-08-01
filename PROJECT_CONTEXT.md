# NiveshakAI Project Context

**Last Updated:** July 31, 2025  
**Branch:** feature-company-analysis  
**Project Status:** Development Phase - Building Core Features

---

## 🎯 **Main Requirements & Objectives**

### **Primary Goal**

Build an AI-powered investment analysis tool that combines fundamental analysis with knowledge from investment books to provide comprehensive stock recommendations.

## **Core Features (5 Most Important)**

### **1. Individual Stock Analysis** ✅

- User provides NSE/BSE stock symbol (e.g., ASIANPAINT, HDFCBANK)
- System fetches current year financial data automatically
- Comprehensive fundamental analysis using template format
- Financial ratio calculations and company profile analysis

### **2. DCF Valuation Engine** ✅

- Intrinsic value calculation with verified formulas
- Uses existing DCF calculation template format
- Multiple scenario analysis with margin of safety
- Clear undervalued/overvalued determination

### **3. Template-Based Reporting** ✅

- Fundamental analysis follows `/templates/fundamental-analysis-template.md`
- DCF analysis follows `/templates/dcf-calculation.md` format
- Consistent structure for professional analysis reports
- Clear buy/hold/sell recommendations

### **4. Symbol-Based Workflow** ✅

- Simple input: Stock symbol (NSE/BSE format)
- Annual reports stored in `/data/annual_reports/SYMBOL-YEAR.pdf` format
- Manual PDF upload required for precise financial data extraction
- Standardized file naming for organized annual report management

### **5. Valuation Assessment** ✅

- Clear overvalued/undervalued determination
- Margin of safety calculations
- Risk assessment and key concerns
- Investment recommendation with rationale

---

## 🏗️ **Current Architecture & Components**

### **Completed Components**

- ✅ **Local RAG Pipeline** - Ollama + Qdrant + Philip Fisher knowledge base
- ✅ **PDF Extraction** - `src/analysis/pdf_extract_and_report.py` for annual report processing
- ✅ **DCF Calculation** - `src/analysis/dcf_calculation.py` with markdown report generation
- ✅ **Analysis Templates** - Data structures in `src/analysis/analysis_template.py`
- ✅ **CLI Interface** - Working commands for analysis and queries

### **Key Files & Their Purpose**

```
src/
├── analysis/
│   ├── dcf_calculation.py          # DCF valuation with report generation
│   ├── pdf_extract_and_report.py   # PDF extraction & basic analysis
│   ├── analysis_template.py        # Data models for structured analysis
│   ├── valuation.py                # Extended valuation methods
│   └── output_formatter.py         # Report formatting utilities
├── cli/
│   └── analyze.py                  # CLI commands for analysis
├── ingestion/
│   └── reports.py                  # PDF text/table extraction utilities
└── embedding/
    └── embedder.py                 # RAG system for knowledge queries
```

### **Working Workflows**

1. **PDF Analysis**: Extract data from annual reports and generate basic analysis
2. **DCF Valuation**: Calculate intrinsic value with markdown reports (e.g., `DummyCo-dcf-2025.md`)
3. **Knowledge Queries**: Ask investment questions using Philip Fisher's principles
4. **CLI Commands**: `python3 -m src.cli.analyze ask|company|compare`

---

## 📊 **Technical Stack**

### **AI & ML**

- **Local LLM**: DeepSeek R1 7B via Ollama (no API costs)
- **Embeddings**: Nomic-embed-text (768 dimensions)
- **Vector DB**: Qdrant (localhost:6333)
- **Knowledge Base**: Philip Fisher's "Common Stocks and Uncommon Profits" (913 chunks)

### **Data Processing**

- **PDF Processing**: pdfplumber for text/table extraction
- **Financial Calculations**: Custom DCF implementation
- **Report Generation**: Markdown templates → PDF/HTML output

### **Configuration**

- **Settings**: `config/settings.yaml` - Ollama integration
- **Templates**: `data/templates/dcf-calculation.md` - DCF report format
- **Dependencies**: All in `requirements.txt`

---

## 🔄 **Current Development Status**

### **Recently Completed (July 2025)**

- ✅ Updated to symbol + PDF-based analysis for accuracy
- ✅ Created symbol-based stock analysis engine requiring annual report PDFs
- ✅ Built workflow: stock symbol + annual report PDF for precise data extraction
- ✅ Integrated DCF calculation with real company financial data from PDFs
- ✅ Template-based analysis using `/templates/fundamental-analysis-template.md`
- ✅ DCF valuation using `/templates/dcf-calculation.md` format
- ✅ Clear overvalued/undervalued determination with accurate financial data
- ✅ Comprehensive reporting with PDF source validation

### **File Status**

- **Active Files**: `pdf_extract_and_report.py`, `dcf_calculation.py`, `analysis_template.py`
- **Deleted**: `company_analysis.py` (was unused in current workflow)
- **Test Files**: `test_template_analysis_fixed.py` (uses analysis_template.py)

---

## 🛠️ **Implementation Roadmap**

### **Phase 1: Symbol-Based Stock Analysis Engine (COMPLETED)**

```python
# IMPLEMENTED: src/analysis/symbol_stock_analyzer.py
- ✅ User input interface for NSE/BSE stock symbols
- ✅ Automated financial data fetching for current year
- ✅ Template-based fundamental analysis report generation
- ✅ Integration with DCF calculation using template format
- ✅ Clear overvalued/undervalued determination
```

**✅ Core Workflow:**

1. User provides: NSE/BSE stock symbol (e.g., ASIANPAINT, HDFCBANK)
2. System looks for annual report in `/data/annual_reports/SYMBOL/year.pdf` format
3. Extract precise financial data from standardized annual report location
4. Generate fundamental analysis using `/templates/fundamental-analysis-template.md`
5. Run DCF valuation using `/templates/dcf-calculation.md` format with extracted data
6. Determine if stock is overvalued or undervalued based on real financials
7. Generate comprehensive analysis report as `SYMBOL-YYYY-MM-DD.md`
8. Provide clear investment recommendation based on actual company performance

**✅ Key Features:**

- Symbol-based input with organized annual report directory structure
- Annual reports organized as `/data/annual_reports/SYMBOL/year.pdf`
- Template-driven consistent reporting with real company data
- Precise DCF calculations using extracted financial statements
- Professional analysis format based on audited financial information
- Report naming: `SYMBOL-YYYY-MM-DD.md` for historical tracking

### **Phase 2: Enhanced Fundamental Analysis**

```python
# TODO: Enhance pdf_extract_and_report.py
- Integrate RAG system for knowledge-based insights
- Apply analysis_template.py structure consistently
- Add Philip Fisher's 15-point checklist automation
```

### **Phase 3: Unified Analysis Pipeline**

```python
# TODO: Create src/analysis/comprehensive_analyzer.py
- Combine PDF extraction + DCF + RAG knowledge
- Generate final buy/hold/sell recommendations
- Create unified report format
```

### **Phase 4: Advanced Features**

- Real-time data integration
- Portfolio optimization
- Risk assessment scoring
- Web interface (Streamlit/FastAPI)

---

## 📝 **Key Inputs & Data Requirements**

### **For DCF Analysis**

```python
# Required inputs for dcf_calculation.py
base_fcf: float                    # Most recent Free Cash Flow
share_capital: float               # From balance sheet
face_value: float                  # Face value per share
total_debt: float                  # Total debt
cash_and_equivalents: float        # Cash position
# Growth rates, discount rate, etc. have defaults
```

### **For Fundamental Analysis**

- Annual report PDFs
- Financial statements (Balance Sheet, P&L, Cash Flow)
- Industry ratios for comparison
- Current market price for valuation

### **Default DCF Parameters**

- FCF Growth (Years 1-5): 10%
- FCF Growth (Years 6-10): 5%
- Terminal Growth: 1%
- Discount Rate: 12%
- Margin of Safety: 30%

---

## 🎯 **Success Metrics**

### **Completed Milestones**

- ✅ Local RAG system operational (no external API dependencies)
- ✅ PDF extraction and basic analysis working
- ✅ DCF calculations with report generation functional
- ✅ Knowledge base queries returning relevant investment insights

### **Next Milestones**

- [ ] Individual stock analysis engine with user input workflow
- [ ] Enhanced fundamental analysis with 3-year trend analysis
- [ ] DCF integration with real company financial data
- [ ] Unified analysis pipeline combining all features
- [ ] Advanced visualizations and dashboards
- [ ] RAG-enhanced investment insights
- [ ] Mobile-responsive web interface

---

## 🔧 **Development Guidelines**

### **Code Organization**

- Keep existing `src/analysis/pdf_extract_and_report.py` as main extraction workflow
- Use `dcf_calculation.py` for all DCF-related calculations
- Maintain `analysis_template.py` for structured data models
- New features should integrate with existing CLI commands

### **Testing**

- Test with dummy datasets before real data
- Verify DCF formulas against financial standards
- Ensure RAG system returns relevant knowledge
- Validate report generation formats

### **Dependencies**

- All dependencies in `requirements.txt`
- Maintain local-first approach (Ollama + Qdrant)
- No external API dependencies for core functionality

---

**This context file should be referenced for all future development decisions and feature implementations.**
