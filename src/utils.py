"""
Consolidated Utilities Module for NiveshakAI
Combines logger, financial_utils, pdf_utils, and fallback_data into a single module
"""

import logging
import logging.handlers
import os
import sys
import math
import statistics
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import yaml

# ============================================================================
# LOGGING UTILITIES (from logger.py)
# ============================================================================

class NiveshakLogger:
    """Centralized logging configuration for NiveshakAI."""
    
    @staticmethod
    def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
        """
        Set up logging configuration for the application.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional log file path
            
        Returns:
            Configured logger instance
        """
        # Create logger
        logger = logging.getLogger("niveshak")
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            try:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file, maxBytes=10*1024*1024, backupCount=5
                )
                file_handler.setLevel(getattr(logging, log_level.upper()))
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Could not set up file logging: {e}")
        
        return logger


# Global logger instance
logger = NiveshakLogger.setup_logging(log_file="logs/niveshak.log")


# ============================================================================
# FINANCIAL UTILITIES (from financial_utils.py)
# ============================================================================

@dataclass
class FinancialStatement:
    """Basic financial statement data structure."""
    period: str
    revenue: float
    net_income: float
    total_assets: float
    total_debt: float
    shareholders_equity: float
    operating_cash_flow: float
    free_cash_flow: float


class FinancialCalculator:
    """Financial calculation utilities."""
    
    @staticmethod
    def calculate_dcf_value(initial_fcf: float, growth_rates: List[float], 
                          terminal_growth: float, discount_rate: float,
                          shares_outstanding: float) -> Dict[str, float]:
        """
        Calculate DCF valuation with given parameters.
        
        Args:
            initial_fcf: Initial free cash flow
            growth_rates: List of growth rates for projection years
            terminal_growth: Terminal growth rate
            discount_rate: Discount rate (WACC)
            shares_outstanding: Number of shares outstanding
            
        Returns:
            Dictionary with valuation results
        """
        try:
            # Project future FCFs
            projected_fcfs = []
            current_fcf = initial_fcf
            
            for rate in growth_rates:
                current_fcf *= (1 + rate)
                projected_fcfs.append(current_fcf)
            
            # Calculate terminal value
            terminal_fcf = projected_fcfs[-1] * (1 + terminal_growth)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth)
            
            # Discount all cash flows to present value
            pv_fcfs = []
            for i, fcf in enumerate(projected_fcfs):
                pv = fcf / ((1 + discount_rate) ** (i + 1))
                pv_fcfs.append(pv)
            
            # Present value of terminal value
            pv_terminal = terminal_value / ((1 + discount_rate) ** len(growth_rates))
            
            # Total enterprise value
            enterprise_value = sum(pv_fcfs) + pv_terminal
            
            # Equity value per share
            equity_value_per_share = enterprise_value / shares_outstanding if shares_outstanding > 0 else 0
            
            return {
                'projected_fcfs': projected_fcfs,
                'terminal_value': terminal_value,
                'present_value_fcfs': pv_fcfs,
                'present_value_terminal': pv_terminal,
                'enterprise_value': enterprise_value,
                'equity_value_per_share': equity_value_per_share,
                'discount_rate': discount_rate,
                'terminal_growth': terminal_growth
            }
            
        except Exception as e:
            logger.error(f"DCF calculation failed: {e}")
            return {'error': str(e)}

    @staticmethod
    def get_risk_free_rate() -> float:
        """
        Get risk-free rate (10-year Treasury).
        
        Returns:
            Risk-free rate as decimal
        """
        # Using historical average 10-year Treasury rate
        # This should be updated with live data in production
        return 0.045  # 4.5%

    @staticmethod
    def get_market_risk_premium() -> float:
        """
        Get market risk premium.
        
        Returns:
            Market risk premium as decimal
        """
        # Based on long-term historical S&P 500 excess returns
        # Typical range is 5-7% above risk-free rate
        return 0.06  # 6%

    @staticmethod
    def calculate_beta(stock_returns: List[float], market_returns: List[float]) -> float:
        """
        Calculate beta coefficient from historical returns.
        
        Args:
            stock_returns: List of stock returns
            market_returns: List of market returns
            
        Returns:
            Beta coefficient
        """
        if len(stock_returns) != len(market_returns) or len(stock_returns) < 2:
            return 1.0  # Default beta
        
        try:
            covariance = statistics.covariance(stock_returns, market_returns)
            market_variance = statistics.variance(market_returns)
            return covariance / market_variance if market_variance > 0 else 1.0
        except Exception:
            return 1.0


# ============================================================================
# PDF UTILITIES (from pdf_utils.py)
# ============================================================================

class PDFProcessor:
    """PDF processing utilities."""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return PDFProcessor.clean_text(text)
        except ImportError:
            logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
            return ""
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - overlap
            
        return [chunk for chunk in chunks if chunk.strip()]
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (basic patterns)
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'\d+\s*$', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,\-\(\)\%\$\:]', '', text)
        
        return text.strip()

    @staticmethod
    def extract_financial_tables(text: str) -> List[Dict[str, Any]]:
        """
        Extract financial tables from text.
        
        Args:
            text: Cleaned text content
            
        Returns:
            List of extracted table data
        """
        tables = []
        
        # Look for common financial statement patterns
        patterns = [
            r'(?i)(income statement|profit.*loss)',
            r'(?i)(balance sheet)',
            r'(?i)(cash flow|statement.*cash flows)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                # Extract surrounding context
                start = max(0, match.start() - 500)
                end = min(len(text), match.end() + 1000)
                context = text[start:end]
                
                tables.append({
                    'type': match.group(1),
                    'content': context,
                    'position': match.start()
                })
        
        return tables


# ============================================================================
# FALLBACK DATA SERVICE (from fallback_data.py)
# ============================================================================

class FallbackDataService:
    """Centralized service for generating fallback financial data."""
    
    @staticmethod
    def get_company_data(symbol: str, data_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Generate fallback financial data for a given company symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'ITC', 'RELIANCE')
            data_type: Type of data needed ('basic', 'comprehensive', 'dcf')
            
        Returns:
            Dictionary containing fallback financial data
        """
        base_data = FallbackDataService._get_base_company_data(symbol)
        
        if data_type == 'basic':
            return FallbackDataService._get_basic_data(base_data)
        elif data_type == 'dcf':
            return FallbackDataService._get_dcf_data(base_data)
        else:
            return FallbackDataService._get_comprehensive_data(base_data)
    
    @staticmethod
    def _get_base_company_data(symbol: str) -> Dict[str, Any]:
        """Get base company information based on symbol."""
        # Enhanced data for known companies
        company_profiles = {
            'ITC': {
                'name': 'ITC Limited',
                'sector': 'Consumer Goods',
                'revenue': 68500,
                'net_profit': 17200,
                'free_cash_flow': 15800,
                'total_debt': 5000,
                'cash_and_equivalents': 8000,
                'shares_outstanding': 1241,
                'roe': 25.1,
                'roce': 28.3,
                'profit_margin': 25.1
            },
            'RELIANCE': {
                'name': 'Reliance Industries Limited',
                'sector': 'Oil & Gas',
                'revenue': 792000,
                'net_profit': 66702,
                'free_cash_flow': 45000,
                'total_debt': 300000,
                'cash_and_equivalents': 200000,
                'shares_outstanding': 676,
                'roe': 12.5,
                'roce': 15.2,
                'profit_margin': 8.4
            }
        }
        
        if symbol.upper() in company_profiles:
            profile = company_profiles[symbol.upper()]
            profile['symbol'] = symbol.upper()
            return profile
        else:
            # Generic template for unknown companies
            return {
                'name': f'{symbol.upper()} Limited',
                'symbol': symbol.upper(),
                'sector': 'General',
                'revenue': 10000,
                'net_profit': 1500,
                'free_cash_flow': 1200,
                'total_debt': 2000,
                'cash_and_equivalents': 1000,
                'shares_outstanding': 100,
                'roe': 15.0,
                'roce': 18.0,
                'profit_margin': 15.0
            }
    
    @staticmethod
    def _get_basic_data(base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return basic market data structure."""
        return {
            'symbol': base_data['symbol'],
            'company_name': base_data['name'],
            'current_price': 100.0,  # Default price
            'market_cap': base_data['revenue'] * 2,
            'pe_ratio': 15.0,
            'data_source': 'FALLBACK_BASIC',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def _get_dcf_data(base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return DCF-specific fallback data."""
        return {
            'symbol': base_data['symbol'],
            'free_cash_flow': base_data['free_cash_flow'],
            'revenue': base_data['revenue'],
            'revenue_growth': 5.0,
            'fcf_margin': (base_data['free_cash_flow'] / base_data['revenue']) * 100,
            'shares_outstanding': base_data['shares_outstanding'],
            'total_debt': base_data['total_debt'],
            'cash_and_equivalents': base_data['cash_and_equivalents'],
            'data_source': 'FALLBACK_DCF'
        }
    
    @staticmethod
    def _get_comprehensive_data(base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return comprehensive fallback data for full analysis."""
        return {
            **base_data,
            'latest_year': '2025',
            'revenue_growth_3yr': 4.5,
            'profit_growth_3yr': 6.0,
            'fcf_growth_3yr': 7.0,
            'debt_to_equity': base_data['total_debt'] / (base_data['revenue'] * 0.5),
            'current_ratio': 1.5,
            'quick_ratio': 1.2,
            'data_source': 'FALLBACK_COMPREHENSIVE',
            'extraction_method': 'UNIFIED_FALLBACK',
            'analysis_quality': 'MEDIUM'
        }


# ============================================================================
# EXPORTS
# ============================================================================

# Make key classes and functions available at module level
__all__ = [
    'logger',
    'NiveshakLogger', 
    'FinancialStatement',
    'FinancialCalculator',
    'PDFProcessor',
    'FallbackDataService'
]
