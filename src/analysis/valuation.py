"""
Financial valuation module for company analysis.

This module handles:
- Discounted Cash Flow (DCF) analysis
- P/E ratio and other multiple-based valuations
- Financial ratio calculations
- Risk assessment and scoring
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from ..utils.financial_utils import (
    calculate_wacc, 
    get_risk_free_rate, 
    get_market_risk_premium,
    calculate_beta
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DCFAssumptions:
    """Assumptions for DCF analysis."""
    terminal_growth_rate: float = 0.025  # 2.5%
    forecast_years: int = 5
    discount_rate: Optional[float] = None  # Will calculate WACC if None
    margin_of_safety: float = 0.30  # 30%


@dataclass
class ValuationResult:
    """Result of a company valuation."""
    company_symbol: str
    valuation_date: datetime
    method: str
    intrinsic_value: float
    current_price: float
    margin_of_safety: float
    recommendation: str  # Buy, Hold, Sell
    confidence_score: float  # 0-1
    assumptions: Dict[str, any]
    detailed_analysis: Dict[str, any]


class DCFAnalyzer:
    """Discounted Cash Flow analysis implementation."""
    
    def __init__(self, assumptions: Optional[DCFAssumptions] = None):
        """Initialize DCF analyzer with assumptions."""
        self.assumptions = assumptions or DCFAssumptions()
        
    def calculate_dcf_value(self, 
                           company_symbol: str,
                           historical_fcf: List[float],
                           revenue_growth_rates: List[float],
                           fcf_margin: float,
                           shares_outstanding: int,
                           debt: float,
                           cash: float,
                           current_price: float) -> ValuationResult:
        """
        Calculate intrinsic value using DCF method.
        
        Args:
            company_symbol: Stock symbol
            historical_fcf: Historical free cash flows (last 3-5 years)
            revenue_growth_rates: Projected revenue growth rates
            fcf_margin: Free cash flow margin
            shares_outstanding: Number of shares outstanding
            debt: Total debt
            cash: Cash and equivalents
            current_price: Current stock price
            
        Returns:
            ValuationResult object
        """
        try:
            logger.info(f"Starting DCF analysis for {company_symbol}")
            
            # Calculate discount rate (WACC)
            discount_rate = self._calculate_discount_rate(company_symbol, debt)
            
            # Project future cash flows
            projected_fcf = self._project_cash_flows(
                historical_fcf, revenue_growth_rates, fcf_margin
            )
            
            # Calculate terminal value
            terminal_value = self._calculate_terminal_value(
                projected_fcf[-1], discount_rate
            )
            
            # Calculate present value
            enterprise_value = self._calculate_present_value(
                projected_fcf, terminal_value, discount_rate
            )
            
            # Calculate equity value
            equity_value = enterprise_value + cash - debt
            intrinsic_value_per_share = equity_value / shares_outstanding
            
            # Apply margin of safety
            target_price = intrinsic_value_per_share * (1 - self.assumptions.margin_of_safety)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(current_price, target_price)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                historical_fcf, revenue_growth_rates
            )
            
            result = ValuationResult(
                company_symbol=company_symbol,
                valuation_date=datetime.now(),
                method="DCF",
                intrinsic_value=intrinsic_value_per_share,
                current_price=current_price,
                margin_of_safety=self.assumptions.margin_of_safety,
                recommendation=recommendation,
                confidence_score=confidence_score,
                assumptions={
                    "discount_rate": discount_rate,
                    "terminal_growth_rate": self.assumptions.terminal_growth_rate,
                    "forecast_years": self.assumptions.forecast_years
                },
                detailed_analysis={
                    "projected_fcf": projected_fcf,
                    "terminal_value": terminal_value,
                    "enterprise_value": enterprise_value,
                    "equity_value": equity_value,
                    "target_price": target_price
                }
            )
            
            logger.info(f"DCF analysis completed for {company_symbol}")
            return result
            
        except Exception as e:
            logger.error(f"DCF analysis failed for {company_symbol}: {str(e)}")
            raise
    
    def _calculate_discount_rate(self, symbol: str, debt: float) -> float:
        """Calculate WACC (Weighted Average Cost of Capital)."""
        if self.assumptions.discount_rate:
            return self.assumptions.discount_rate
        
        # TODO: Implement WACC calculation
        # This should include risk-free rate, market risk premium, beta, etc.
        return 0.10  # Default 10%
    
    def _project_cash_flows(self, 
                           historical_fcf: List[float], 
                           growth_rates: List[float],
                           fcf_margin: float) -> List[float]:
        """Project future free cash flows."""
        if not historical_fcf:
            raise ValueError("Historical FCF data is required")
        
        base_fcf = historical_fcf[-1]  # Most recent FCF
        projected_fcf = []
        
        for i, growth_rate in enumerate(growth_rates[:self.assumptions.forecast_years]):
            if i == 0:
                fcf = base_fcf * (1 + growth_rate)
            else:
                fcf = projected_fcf[-1] * (1 + growth_rate)
            projected_fcf.append(fcf)
        
        return projected_fcf
    
    def _calculate_terminal_value(self, final_year_fcf: float, discount_rate: float) -> float:
        """Calculate terminal value using Gordon Growth Model."""
        terminal_growth = self.assumptions.terminal_growth_rate
        terminal_value = (final_year_fcf * (1 + terminal_growth)) / (discount_rate - terminal_growth)
        return terminal_value
    
    def _calculate_present_value(self, 
                               projected_fcf: List[float], 
                               terminal_value: float, 
                               discount_rate: float) -> float:
        """Calculate present value of cash flows and terminal value."""
        pv_cash_flows = sum(
            fcf / ((1 + discount_rate) ** (i + 1))
            for i, fcf in enumerate(projected_fcf)
        )
        
        pv_terminal_value = terminal_value / ((1 + discount_rate) ** len(projected_fcf))
        
        return pv_cash_flows + pv_terminal_value
    
    def _generate_recommendation(self, current_price: float, target_price: float) -> str:
        """Generate buy/hold/sell recommendation."""
        if current_price <= target_price:
            return "Buy"
        elif current_price <= target_price * 1.1:  # Within 10% of target
            return "Hold"
        else:
            return "Sell"
    
    def _calculate_confidence_score(self, 
                                  historical_fcf: List[float], 
                                  growth_rates: List[float]) -> float:
        """Calculate confidence score based on data quality and consistency."""
        # TODO: Implement confidence scoring algorithm
        # Consider factors like FCF consistency, growth rate reasonableness, etc.
        return 0.75  # Placeholder


class MultipleValuation:
    """Multiple-based valuation methods (P/E, P/B, etc.)."""
    
    def calculate_pe_valuation(self, 
                              earnings_per_share: float,
                              industry_pe: float,
                              growth_rate: float,
                              current_price: float) -> ValuationResult:
        """Calculate valuation using P/E ratio method."""
        # Adjust P/E for growth (PEG considerations)
        adjusted_pe = industry_pe * (1 + growth_rate / 100)
        intrinsic_value = earnings_per_share * adjusted_pe
        
        recommendation = "Buy" if current_price < intrinsic_value * 0.9 else "Hold"
        
        return ValuationResult(
            company_symbol="",  # To be filled by caller
            valuation_date=datetime.now(),
            method="P/E Multiple",
            intrinsic_value=intrinsic_value,
            current_price=current_price,
            margin_of_safety=0.10,
            recommendation=recommendation,
            confidence_score=0.6,  # Lower confidence for multiple-based methods
            assumptions={"industry_pe": industry_pe, "growth_rate": growth_rate},
            detailed_analysis={"adjusted_pe": adjusted_pe}
        )
    
    def calculate_book_value_ratio(self, 
                                  book_value_per_share: float,
                                  industry_pb: float,
                                  current_price: float) -> ValuationResult:
        """Calculate valuation using P/B ratio method."""
        intrinsic_value = book_value_per_share * industry_pb
        recommendation = "Buy" if current_price < intrinsic_value * 0.8 else "Hold"
        
        return ValuationResult(
            company_symbol="",
            valuation_date=datetime.now(),
            method="P/B Multiple",
            intrinsic_value=intrinsic_value,
            current_price=current_price,
            margin_of_safety=0.20,
            recommendation=recommendation,
            confidence_score=0.5,
            assumptions={"industry_pb": industry_pb},
            detailed_analysis={}
        )


class RiskAssessment:
    """Risk assessment and scoring for investments."""
    
    def calculate_risk_score(self, 
                           company_data: Dict[str, any],
                           market_data: Dict[str, any]) -> Dict[str, float]:
        """
        Calculate comprehensive risk score for a company.
        
        Returns:
            Dictionary with risk scores for different categories
        """
        risk_scores = {
            "financial_risk": self._assess_financial_risk(company_data),
            "market_risk": self._assess_market_risk(market_data),
            "business_risk": self._assess_business_risk(company_data),
            "overall_risk": 0.0
        }
        
        # Calculate weighted overall risk
        risk_scores["overall_risk"] = (
            risk_scores["financial_risk"] * 0.4 +
            risk_scores["market_risk"] * 0.3 +
            risk_scores["business_risk"] * 0.3
        )
        
        return risk_scores
    
    def _assess_financial_risk(self, data: Dict[str, any]) -> float:
        """Assess financial risk based on debt ratios, liquidity, etc."""
        # TODO: Implement financial risk assessment
        return 0.5  # Placeholder (0 = low risk, 1 = high risk)
    
    def _assess_market_risk(self, data: Dict[str, any]) -> float:
        """Assess market risk based on volatility, beta, etc."""
        # TODO: Implement market risk assessment
        return 0.4  # Placeholder
    
    def _assess_business_risk(self, data: Dict[str, any]) -> float:
        """Assess business risk based on industry, competition, etc."""
        # TODO: Implement business risk assessment
        return 0.3  # Placeholder


def create_dcf_analyzer(config_path: str = "config/persona.yaml") -> DCFAnalyzer:
    """Create DCF analyzer with user's investment preferences."""
    # TODO: Load user preferences and create customized DCF assumptions
    return DCFAnalyzer()


def save_valuation_result(result: ValuationResult, output_dir: str = "data/valuations") -> str:
    """Save valuation result to JSON file."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{result.company_symbol}_{result.method}_{result.valuation_date.strftime('%Y%m%d')}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Convert result to dict for JSON serialization
    result_dict = {
        "company_symbol": result.company_symbol,
        "valuation_date": result.valuation_date.isoformat(),
        "method": result.method,
        "intrinsic_value": result.intrinsic_value,
        "current_price": result.current_price,
        "margin_of_safety": result.margin_of_safety,
        "recommendation": result.recommendation,
        "confidence_score": result.confidence_score,
        "assumptions": result.assumptions,
        "detailed_analysis": result.detailed_analysis
    }
    
    with open(filepath, 'w') as f:
        json.dump(result_dict, f, indent=2)
    
    return filepath
