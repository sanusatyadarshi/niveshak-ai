"""
Annual report ingestion module for processing company financial reports.

This module handles:
- Annual report PDF parsing and text extraction
- Financial statement extraction (Income Statement, Balance Sheet, Cash Flow)
- Key financial metrics calculation
- Structured data storage for analysis
"""

import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml
from dataclasses import dataclass
from datetime import datetime
import pdfplumber
import pandas as pd

from ..utils.pdf_utils import extract_text_from_pdf, extract_tables_from_pdf
from ..utils.financial_utils import parse_financial_statement, extract_financial_metrics
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FinancialStatement:
    """Represents a financial statement from an annual report."""
    company_symbol: str
    report_year: int
    statement_type: str  # income_statement, balance_sheet, cash_flow
    data: Dict[str, float]
    raw_text: str


@dataclass
class AnnualReport:
    """Represents a complete annual report."""
    company_symbol: str
    company_name: str
    report_year: int
    filing_date: datetime
    income_statement: Optional[FinancialStatement]
    balance_sheet: Optional[FinancialStatement]
    cash_flow: Optional[FinancialStatement]
    key_metrics: Dict[str, float]
    raw_text: str
    source_file: str


class ReportIngester:
    """Handles ingestion of annual reports into structured format."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize the report ingester with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.reports_dir = Path(self.config['storage']['reports_dir'])
        
    def ingest_report(self, file_path: str, company_symbol: str, report_year: int) -> Optional[AnnualReport]:
        """
        Ingest a single annual report.
        
        Args:
            file_path: Path to the annual report PDF
            company_symbol: Stock symbol (e.g., 'AAPL')
            report_year: Year of the report
            
        Returns:
            AnnualReport object if successful, None otherwise
        """
        try:
            logger.info(f"Starting ingestion of report: {file_path} for {company_symbol}")
            
            # Extract text and tables from PDF
            raw_text = extract_text_from_pdf(file_path)
            tables = extract_tables_from_pdf(file_path)
            
            # Parse financial statements
            income_statement = self._parse_income_statement(raw_text, tables, company_symbol, report_year)
            balance_sheet = self._parse_balance_sheet(raw_text, tables, company_symbol, report_year)
            cash_flow = self._parse_cash_flow(raw_text, tables, company_symbol, report_year)
            
            # Calculate key metrics
            key_metrics = self._calculate_key_metrics(income_statement, balance_sheet, cash_flow)
            
            # Create annual report object
            report = AnnualReport(
                company_symbol=company_symbol,
                company_name=self._extract_company_name(raw_text),
                report_year=report_year,
                filing_date=datetime.now(),  # TODO: Extract actual filing date
                income_statement=income_statement,
                balance_sheet=balance_sheet,
                cash_flow=cash_flow,
                key_metrics=key_metrics,
                raw_text=raw_text,
                source_file=file_path
            )
            
            # Save structured report
            self._save_report(report)
            
            logger.info(f"Successfully ingested report for {company_symbol}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to ingest report {file_path}: {str(e)}")
            return None
    
    def ingest_reports_from_directory(self, directory: str) -> List[AnnualReport]:
        """
        Ingest all reports from a directory.
        
        Args:
            directory: Path to directory containing reports
            
        Returns:
            List of successfully processed reports
        """
        reports = []
        reports_dir = Path(directory)
        
        for file_path in reports_dir.glob("*.pdf"):
            # Try to extract company symbol and year from filename
            symbol, year = self._parse_filename(file_path.name)
            if symbol and year:
                report = self.ingest_report(str(file_path), symbol, year)
                if report:
                    reports.append(report)
                    
        return reports
    
    def _parse_income_statement(self, text: str, tables: List, symbol: str, year: int) -> Optional[FinancialStatement]:
        """Parse income statement from report text and tables."""
        # TODO: Implement income statement parsing logic
        return FinancialStatement(
            company_symbol=symbol,
            report_year=year,
            statement_type="income_statement",
            data={},
            raw_text=""
        )
    
    def _parse_balance_sheet(self, text: str, tables: List, symbol: str, year: int) -> Optional[FinancialStatement]:
        """Parse balance sheet from report text and tables."""
        # TODO: Implement balance sheet parsing logic
        return FinancialStatement(
            company_symbol=symbol,
            report_year=year,
            statement_type="balance_sheet",
            data={},
            raw_text=""
        )
    
    def _parse_cash_flow(self, text: str, tables: List, symbol: str, year: int) -> Optional[FinancialStatement]:
        """Parse cash flow statement from report text and tables."""
        # TODO: Implement cash flow parsing logic
        return FinancialStatement(
            company_symbol=symbol,
            report_year=year,
            statement_type="cash_flow",
            data={},
            raw_text=""
        )
    
    def _calculate_key_metrics(self, income: Optional[FinancialStatement], 
                             balance: Optional[FinancialStatement], 
                             cash_flow: Optional[FinancialStatement]) -> Dict[str, float]:
        """Calculate key financial metrics from statements."""
        # TODO: Implement financial metrics calculation
        return {}
    
    def _extract_company_name(self, text: str) -> str:
        """Extract company name from report text."""
        # TODO: Implement company name extraction
        return ""
    
    def _parse_filename(self, filename: str) -> tuple[Optional[str], Optional[int]]:
        """Parse company symbol and year from filename."""
        # Example: AAPL_2023_10K.pdf -> ('AAPL', 2023)
        # TODO: Implement filename parsing logic
        return None, None
    
    def _save_report(self, report: AnnualReport) -> None:
        """Save structured report to JSON file."""
        output_file = self.reports_dir / f"{report.company_symbol}_{report.report_year}_structured.json"
        
        # Convert dataclass to dict for JSON serialization
        report_dict = {
            'company_symbol': report.company_symbol,
            'company_name': report.company_name,
            'report_year': report.report_year,
            'filing_date': report.filing_date.isoformat(),
            'key_metrics': report.key_metrics,
            'source_file': report.source_file
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_dict, f, indent=2)


def list_available_reports(reports_dir: str = "data/reports") -> List[Dict[str, Any]]:
    """
    List all available reports in the reports directory.
    
    Returns:
        List of report information dictionaries
    """
    reports = []
    reports_path = Path(reports_dir)
    
    # List PDF files
    for file_path in reports_path.glob("*.pdf"):
        reports.append({
            'filename': file_path.name,
            'path': str(file_path),
            'size_mb': file_path.stat().st_size / (1024 * 1024),
            'type': 'pdf'
        })
    
    # List structured JSON files
    for file_path in reports_path.glob("*_structured.json"):
        reports.append({
            'filename': file_path.name,
            'path': str(file_path),
            'size_mb': file_path.stat().st_size / (1024 * 1024),
            'type': 'structured'
        })
    
    return reports


def get_company_reports(company_symbol: str, reports_dir: str = "data/reports") -> List[Dict[str, Any]]:
    """
    Get all reports for a specific company.
    
    Args:
        company_symbol: Stock symbol (e.g., 'AAPL')
        reports_dir: Directory containing reports
        
    Returns:
        List of report files for the company
    """
    reports = []
    reports_path = Path(reports_dir)
    
    pattern = f"{company_symbol}_*"
    for file_path in reports_path.glob(pattern):
        reports.append({
            'filename': file_path.name,
            'path': str(file_path),
            'company': company_symbol
        })
    
    return reports


class ReportExtractor:
    @staticmethod
    def extract_text_sections(pdf_path):
        sections = {}
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            # Optionally, split into sections using regex/keywords
            sections['full_text'] = full_text
        return sections

    @staticmethod
    def extract_tables(pdf_path):
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    df = pd.DataFrame(table[1:], columns=table[0])
                    tables.append(df)
        return tables

    @staticmethod
    def extract_csv(csv_path):
        return pd.read_csv(csv_path)
