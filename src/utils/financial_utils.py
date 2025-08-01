"""
Financial utilities for calculations and analysis.

This module provides functions for:
- Financial ratio calculations
- WACC and discount rate calculations
- Cash flow analysis
- Risk metrics calculation
- Data validation and formatting
"""

import math
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class FinancialStatement:
    """Basic financial statement data structure."""
    revenue: float
    net_income: float
    total_assets: float
    total_liabilities: float
    shareholders_equity: float
    cash_and_equivalents: float
    operating_cash_flow: float
    free_cash_flow: float


@dataclass
class StockData:
    """Stock market data structure."""
    symbol: str
    current_price: float
    market_cap: float
    shares_outstanding: int
    beta: float
    dividend_yield: float
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None


def calculate_financial_ratios(statement: FinancialStatement) -> Dict[str, float]:
    """
    Calculate key financial ratios from financial statement data.
    
    Args:
        statement: Financial statement data
        
    Returns:
        Dictionary of calculated ratios
    """
    ratios = {}
    
    try:
        # Profitability Ratios
        if statement.revenue > 0:
            ratios['net_margin'] = statement.net_income / statement.revenue
            ratios['operating_margin'] = statement.operating_cash_flow / statement.revenue
        
        if statement.total_assets > 0:
            ratios['roa'] = statement.net_income / statement.total_assets  # Return on Assets
            ratios['asset_turnover'] = statement.revenue / statement.total_assets
        
        if statement.shareholders_equity > 0:
            ratios['roe'] = statement.net_income / statement.shareholders_equity  # Return on Equity
        
        # Liquidity Ratios
        current_assets = statement.cash_and_equivalents  # Simplified - would need more data
        current_liabilities = statement.total_liabilities * 0.6  # Estimated current portion
        
        if current_liabilities > 0:
            ratios['current_ratio'] = current_assets / current_liabilities
        
        # Leverage Ratios
        if statement.shareholders_equity > 0:
            ratios['debt_to_equity'] = statement.total_liabilities / statement.shareholders_equity
        
        if statement.total_assets > 0:
            ratios['debt_ratio'] = statement.total_liabilities / statement.total_assets
        
        # Efficiency Ratios
        if statement.total_assets > 0 and statement.shareholders_equity > 0:
            ratios['equity_multiplier'] = statement.total_assets / statement.shareholders_equity
        
        logger.info("Financial ratios calculated successfully")
        
    except Exception as e:
        logger.error(f"Error calculating financial ratios: {str(e)}")
    
    return ratios


def calculate_wacc(risk_free_rate: float,
                   market_risk_premium: float,
                   beta: float,
                   debt_to_equity: float,
                   tax_rate: float = 0.25,
                   cost_of_debt: float = 0.05) -> float:
    """
    Calculate Weighted Average Cost of Capital (WACC).
    
    Args:
        risk_free_rate: Risk-free interest rate (e.g., 10-year treasury)
        market_risk_premium: Market risk premium
        beta: Stock's beta coefficient
        debt_to_equity: Debt-to-equity ratio
        tax_rate: Corporate tax rate
        cost_of_debt: Cost of debt
        
    Returns:
        WACC as decimal (e.g., 0.10 for 10%)
    """
    try:
        # Calculate cost of equity using CAPM
        cost_of_equity = risk_free_rate + beta * market_risk_premium
        
        # Calculate after-tax cost of debt
        after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
        
        # Calculate weights
        total_capital = 1 + debt_to_equity  # Equity = 1, Debt = debt_to_equity
        weight_equity = 1 / total_capital
        weight_debt = debt_to_equity / total_capital
        
        # Calculate WACC
        wacc = (weight_equity * cost_of_equity) + (weight_debt * after_tax_cost_of_debt)
        
        logger.info(f"WACC calculated: {wacc:.2%}")
        return wacc
        
    except Exception as e:
        logger.error(f"Error calculating WACC: {str(e)}")
        return 0.10  # Default return


def get_risk_free_rate() -> float:
    """
    Get current risk-free rate (10-year Treasury rate).
    
    Note: This is a placeholder. In production, this would fetch
    real-time data from a financial API.
    
    Returns:
        Risk-free rate as decimal
    """
    # Using historical average 10-year Treasury rate
    # This should be updated with live data in production
    return 0.045  # 4.5%


def get_market_risk_premium() -> float:
    """
    Get market risk premium.
    
    Note: This is a placeholder. In production, this would be
    calculated from historical market data.
    
    Returns:
        Market risk premium as decimal
    """
    # Based on long-term historical S&P 500 excess returns
    # Typical range is 5-7% above risk-free rate
    return 0.06  # 6%


def calculate_beta(stock_returns: List[float], market_returns: List[float]) -> float:
    """
    Calculate beta coefficient from historical returns.
    
    Args:
        stock_returns: List of stock returns (as decimals)
        market_returns: List of market returns (as decimals)
        
    Returns:
        Beta coefficient
    """
    try:
        if len(stock_returns) != len(market_returns) or len(stock_returns) < 2:
            logger.warning("Insufficient data for beta calculation")
            return 1.0  # Market beta
        
        # Calculate covariance and variance
        stock_mean = statistics.mean(stock_returns)
        market_mean = statistics.mean(market_returns)
        
        covariance = sum((s - stock_mean) * (m - market_mean) 
                        for s, m in zip(stock_returns, market_returns)) / (len(stock_returns) - 1)
        
        market_variance = statistics.variance(market_returns)
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        
        logger.info(f"Beta calculated: {beta:.2f}")
        return beta
        
    except Exception as e:
        logger.error(f"Error calculating beta: {str(e)}")
        return 1.0


def calculate_dcf_value(cash_flows: List[float],
                       terminal_value: float,
                       discount_rate: float) -> float:
    """
    Calculate present value of cash flows for DCF analysis.
    
    Args:
        cash_flows: List of projected cash flows
        terminal_value: Terminal value at end of projection period
        discount_rate: Discount rate (WACC)
        
    Returns:
        Present value of all cash flows
    """
    try:
        present_value = 0
        
        # Present value of projected cash flows
        for i, cf in enumerate(cash_flows, 1):
            pv = cf / ((1 + discount_rate) ** i)
            present_value += pv
        
        # Present value of terminal value
        terminal_pv = terminal_value / ((1 + discount_rate) ** len(cash_flows))
        present_value += terminal_pv
        
        logger.info(f"DCF present value calculated: ${present_value:,.0f}")
        return present_value
        
    except Exception as e:
        logger.error(f"Error calculating DCF value: {str(e)}")
        return 0


def project_cash_flows(historical_cf: List[float],
                      growth_rates: List[float]) -> List[float]:
    """
    Project future cash flows based on historical data and growth rates.
    
    Args:
        historical_cf: Historical cash flows (most recent first)
        growth_rates: Growth rates for projection years
        
    Returns:
        List of projected cash flows
    """
    try:
        if not historical_cf:
            raise ValueError("Historical cash flows required")
        
        base_cf = historical_cf[0]  # Most recent cash flow
        projected_cf = []
        
        for i, growth_rate in enumerate(growth_rates):
            if i == 0:
                cf = base_cf * (1 + growth_rate)
            else:
                cf = projected_cf[-1] * (1 + growth_rate)
            projected_cf.append(cf)
        
        logger.info(f"Projected {len(projected_cf)} years of cash flows")
        return projected_cf
        
    except Exception as e:
        logger.error(f"Error projecting cash flows: {str(e)}")
        return []


def calculate_terminal_value(final_cf: float,
                           terminal_growth_rate: float,
                           discount_rate: float) -> float:
    """
    Calculate terminal value using Gordon Growth Model.
    
    Args:
        final_cf: Final year cash flow
        terminal_growth_rate: Long-term growth rate
        discount_rate: Discount rate
        
    Returns:
        Terminal value
    """
    try:
        if discount_rate <= terminal_growth_rate:
            raise ValueError("Discount rate must be greater than terminal growth rate")
        
        terminal_value = (final_cf * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
        
        logger.info(f"Terminal value calculated: ${terminal_value:,.0f}")
        return terminal_value
        
    except Exception as e:
        logger.error(f"Error calculating terminal value: {str(e)}")
        return 0


def parse_financial_statement(data: Dict[str, any]) -> Optional[FinancialStatement]:
    """
    Parse financial statement data from various sources.
    
    Args:
        data: Raw financial data dictionary
        
    Returns:
        FinancialStatement object or None if parsing fails
    """
    try:
        # This would handle parsing from different data sources
        # (SEC filings, APIs, etc.)
        
        # Placeholder implementation
        statement = FinancialStatement(
            revenue=data.get('revenue', 0),
            net_income=data.get('net_income', 0),
            total_assets=data.get('total_assets', 0),
            total_liabilities=data.get('total_liabilities', 0),
            shareholders_equity=data.get('shareholders_equity', 0),
            cash_and_equivalents=data.get('cash', 0),
            operating_cash_flow=data.get('operating_cf', 0),
            free_cash_flow=data.get('free_cf', 0)
        )
        
        return statement
        
    except Exception as e:
        logger.error(f"Error parsing financial statement: {str(e)}")
        return None


def extract_financial_metrics(text: str) -> Dict[str, float]:
    """
    Extract financial metrics from text (e.g., annual report text).
    
    Args:
        text: Text containing financial information
        
    Returns:
        Dictionary of extracted metrics
    """
    metrics = {}
    
    try:
        import re
        
        # Define patterns for common financial metrics
        patterns = {
            'revenue': r'(?:revenue|net sales|total revenue)[:\s]+\$?(\d+(?:,\d+)*(?:\.\d+)?)',
            'net_income': r'(?:net income|earnings)[:\s]+\$?(\d+(?:,\d+)*(?:\.\d+)?)',
            'total_assets': r'(?:total assets)[:\s]+\$?(\d+(?:,\d+)*(?:\.\d+)?)',
            'cash': r'(?:cash and cash equivalents|cash)[:\s]+\$?(\d+(?:,\d+)*(?:\.\d+)?)'
        }
        
        for metric, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value_str = match.group(1).replace(',', '')
                try:
                    value = float(value_str)
                    metrics[metric] = value
                    break  # Take first match
                except ValueError:
                    continue
        
        logger.info(f"Extracted {len(metrics)} financial metrics from text")
        
    except Exception as e:
        logger.error(f"Error extracting financial metrics: {str(e)}")
    
    return metrics


def validate_financial_data(data: Dict[str, float]) -> Tuple[bool, List[str]]:
    """
    Validate financial data for consistency and reasonableness.
    
    Args:
        data: Financial data dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        # Check for negative values where inappropriate
        non_negative_fields = ['revenue', 'total_assets', 'cash']
        for field in non_negative_fields:
            if field in data and data[field] < 0:
                errors.append(f"{field} cannot be negative")
        
        # Check balance sheet equation: Assets = Liabilities + Equity
        if all(field in data for field in ['total_assets', 'total_liabilities', 'shareholders_equity']):
            assets = data['total_assets']
            liabilities_equity = data['total_liabilities'] + data['shareholders_equity']
            tolerance = 0.01  # 1% tolerance
            
            if abs(assets - liabilities_equity) / assets > tolerance:
                errors.append("Balance sheet equation does not balance")
        
        # Check for reasonable ratios
        if 'revenue' in data and 'total_assets' in data and data['total_assets'] > 0:
            asset_turnover = data['revenue'] / data['total_assets']
            if asset_turnover > 10:  # Very high asset turnover
                errors.append("Asset turnover ratio appears unusually high")
        
        is_valid = len(errors) == 0
        
    except Exception as e:
        logger.error(f"Error validating financial data: {str(e)}")
        errors.append(f"Validation error: {str(e)}")
        is_valid = False
    
    return is_valid, errors


def format_financial_number(value: float, format_type: str = "currency") -> str:
    """
    Format financial numbers for display.
    
    Args:
        value: Numerical value
        format_type: Format type ('currency', 'percentage', 'ratio')
        
    Returns:
        Formatted string
    """
    try:
        if format_type == "currency":
            if abs(value) >= 1e9:
                return f"${value/1e9:.1f}B"
            elif abs(value) >= 1e6:
                return f"${value/1e6:.1f}M"
            elif abs(value) >= 1e3:
                return f"${value/1e3:.1f}K"
            else:
                return f"${value:,.0f}"
        
        elif format_type == "percentage":
            return f"{value:.1%}"
        
        elif format_type == "ratio":
            return f"{value:.2f}"
        
        else:
            return f"{value:,.2f}"
            
    except Exception as e:
        logger.error(f"Error formatting number: {str(e)}")
        return str(value)
