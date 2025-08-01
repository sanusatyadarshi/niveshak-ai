"""
Script: pdf_extract_and_report.py
Purpose: Extract structured data from an annual report PDF and generate a sanitized PDF report using the analysis template.
"""
import os
import re
import pdfplumber
import pandas as pd
from fpdf import FPDF

def extract_sections_and_tables(pdf_path):
    """Extracts text sections and tables from a PDF, associating tables with section headers."""
    sections = {}
    tables = []
    section_patterns = [
        r"Management Discussion and Analysis", r"Balance Sheet", r"Profit and Loss",
        r"Cash Flow Statement", r"Notes to Accounts", r"Auditor's Report",
        r"Financial Highlights", r"Corporate Governance"
    ]
    pattern = r"(" + r"|".join(section_patterns) + r")"
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            full_text += page_text + "\n"
        # Section splitting
        matches = list(re.finditer(pattern, full_text, re.IGNORECASE))
        for i, match in enumerate(matches):
            section_name = match.group(0).strip()
            start = match.start()
            end = matches[i+1].start() if i+1 < len(matches) else len(full_text)
            sections[section_name] = full_text[start:end].strip()
        sections['full_text'] = full_text
        # Table extraction
        last_section = None
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            section_header = None
            for pat in section_patterns:
                if re.search(pat, page_text, re.IGNORECASE):
                    section_header = pat
                    last_section = pat
                    break
            for table in page.extract_tables():
                # Handle multi-line headers
                if len(table) > 1 and any('\n' in str(cell) for cell in table[0]):
                    header = [' '.join(filter(None, [str(cell).replace('\n', ' ').strip() for cell in row]))
                              for row in zip(table[0], table[1])]
                    data = table[2:]
                else:
                    header = table[0]
                    data = table[1:]
                df = pd.DataFrame(data, columns=header)
                tables.append({'section': section_header or last_section, 'table': df})
    return sections, tables

def sanitize(text):
    """Remove emojis and non-ASCII characters for PDF output."""
    return text.encode('ascii', 'ignore').decode()

def generate_pdf_report(template_data, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Title
    pdf.cell(0, 10, sanitize(f"Stock Analysis Report - {template_data['company_name']}"), ln=True, align='C')
    pdf.ln(5)
    # Section 1: Business & Qualitative
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Section 1: Business & Qualitative Analysis", ln=True)
    pdf.set_font("Arial", size=10)
    for q, a in template_data['business_analysis'].items():
        pdf.multi_cell(0, 8, sanitize(f"{q}: {a}"))
    pdf.ln(3)
    # Section 2: Financial Metrics
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Section 2: Financial Metrics & Judgement", ln=True)
    pdf.set_font("Arial", size=10)
    for metric, value in template_data['financial_metrics'].items():
        pdf.cell(0, 8, sanitize(f"{metric}: {value}"), ln=True)
    pdf.ln(3)
    # Section 3: Ratio Analysis
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Section 3: Ratio Analysis", ln=True)
    pdf.set_font("Arial", size=10)
    for ratio, value in template_data['ratio_analysis'].items():
        pdf.cell(0, 8, sanitize(f"{ratio}: {value}"), ln=True)
    pdf.ln(5)
    # Recommendation
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Investment Recommendation", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, sanitize(template_data['recommendation']))
    pdf.output(output_path)

# Example usage (to be replaced with your pipeline logic):
if __name__ == "__main__":
    pdf_path = "data/annual_reports/ITC-2024.pdf"
    output_pdf = "reports/ITC_Stock_Analysis_FY23-24.pdf"
    print(f"[DEBUG] Checking if input PDF exists: {pdf_path} ...")
    if not os.path.exists(pdf_path):
        print(f"[ERROR] Input PDF not found: {pdf_path}")
        exit(1)
    print("[DEBUG] Extracting sections and tables...")
    try:
        sections, tables = extract_sections_and_tables(pdf_path)
        print(f"[DEBUG] Extracted {len(sections)} sections and {len(tables)} tables.")
    except Exception as e:
        print(f"[ERROR] Failed to extract from PDF: {e}")
        exit(1)

    def find_in_sections(keywords):
        for section, text in sections.items():
            for kw in keywords:
                match = re.search(rf"{kw}(.{{0,100}})", text, re.IGNORECASE)
                if match:
                    return match.group(0).strip()
        return "[Not found]"

    business_questions = [
        "What does the company do?", "Who are its promoters?", "What do they manufacture?", "How many plants do they have and where?", "What kind of raw material is required?", "Who are the company's clients or end users?", "Who are their competitors?", "Who are the major shareholders of the company?", "Do they plan to launch any new products?", "Do they plan to expand to other countries?", "What is the revenue mix? Which product sells the most?", "Do they operate under a heavy regulatory environment?", "Who are their bankers, auditors?", "How many employees do they have? Labour issues?", "What are the entry barriers for new participants?", "Are products easily replicable in cheap-labor countries?", "Too many subsidiaries?"
    ]
    business_analysis = {}
    for q in business_questions:
        keywords = [w for w in re.findall(r'\w+', q) if len(w) > 3]
        business_analysis[q] = find_in_sections(keywords)

    def extract_metric_from_tables(metric_keywords):
        for entry in tables:
            df = entry['table']
            if df.empty:
                continue
            for col in df.columns:
                for kw in metric_keywords:
                    if kw.lower() in str(col).lower():
                        non_empty = df[col].dropna()
                        if not non_empty.empty:
                            val = non_empty.iloc[0]
                            return str(val)
        return "N/A"

    financial_metrics = {
        "Gross Profit Margin": extract_metric_from_tables(["gross profit", "gpm"]),
        "Revenue Growth": extract_metric_from_tables(["revenue growth", "sales growth", "revenue"]),
        "Return on Equity": extract_metric_from_tables(["return on equity", "roe"]),
        "Debt Level": extract_metric_from_tables(["debt", "debt to equity"]),
        "Cash Flow Operations": extract_metric_from_tables(["cash flow", "operating cash flow"])
    }
    ratio_analysis = {
        "Current Ratio": extract_metric_from_tables(["current ratio"]),
        "Quick Ratio": extract_metric_from_tables(["quick ratio"]),
        "ROE": extract_metric_from_tables(["roe", "return on equity"]),
        "ROA": extract_metric_from_tables(["roa", "return on assets"]),
        "Debt to Equity": extract_metric_from_tables(["debt to equity"]),
        "Interest Coverage": extract_metric_from_tables(["interest coverage"])
    }
    recommendation = 'Decision: [Auto-filled for demo]\nConfidence: [Demo]\nReasoning: [Demo extraction only]'

    template_data = {
        'company_name': 'ITC Limited',
        'business_analysis': business_analysis,
        'financial_metrics': financial_metrics,
        'ratio_analysis': ratio_analysis,
        'recommendation': recommendation
    }
    try:
        generate_pdf_report(template_data, output_pdf)
        print(f"[SUCCESS] PDF report generated: {os.path.abspath(output_pdf)}")
    except Exception as e:
        print(f"[ERROR] Failed to generate PDF: {e}")
        exit(1)
