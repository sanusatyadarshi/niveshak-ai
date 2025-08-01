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

def extract_and_analyze_pdf(pdf_path: str):
    """
    Main function to extract and analyze PDF financial data
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary with extracted financial data
    """
    try:
        sections, tables = extract_sections_and_tables(pdf_path)
        
        if not sections or not tables:
            return None
            
        # Basic extraction logic - can be enhanced
        return {
            'data_source': 'PDF_EXTRACTED',
            'sections_count': len(sections),
            'tables_count': len(tables),
            'extraction_success': True
        }
    except Exception as e:
        print(f"[ERROR] PDF extraction failed: {e}")
        return None


if __name__ == "__main__":
    # Simple test of PDF extraction
    pdf_path = "data/annual_reports/ITC/2024.pdf"
    result = extract_and_analyze_pdf(pdf_path)
    if result:
        print(f"[SUCCESS] Extracted {result['sections_count']} sections and {result['tables_count']} tables")
    else:
        print("[ERROR] PDF extraction failed")
