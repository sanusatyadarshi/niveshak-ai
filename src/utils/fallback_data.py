"""
Unified Fallback Data Service
Consolidates all fallback data generation into a single, maintainable location.
"""
from typing import Dict, Any
from datetime import datetime

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
