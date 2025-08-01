"""
Valuation Analysis Module

This module provides comprehensive valuation methods including:
- DCF (Discounted Cash Flow) Analysis
- Relative Valuation (P/E, P/B, P/S ratios)
- Risk Assessment
- Investment Recommendations
"""

from typing import Dict, Any, List, Tuple
import math
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DCFAnalyzer:
    """
    Discounted Cash Flow (DCF) Analyzer
    
    Performs intrinsic value calculation using DCF methodology
    """
    
    def __init__(self, discount_rate: float = 0.12, terminal_growth_rate: float = 0.02):
        """
        Initialize DCF Analyzer
        
        Args:
            discount_rate: WACC or required rate of return (default 12%)
            terminal_growth_rate: Long-term growth rate (default 2%)
        """
        self.discount_rate = discount_rate
        self.terminal_growth_rate = terminal_growth_rate
        
    def calculate_dcf_valuation(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate DCF valuation for a company
        
        Args:
            financial_data: Dictionary containing financial metrics
            
        Returns:
            Dictionary with DCF analysis results
        """
        try:
            # Extract key financial metrics
            fcf = financial_data.get('free_cash_flow', 0)  # in Cr
            revenue = financial_data.get('revenue', 0)  # in Cr
            shares_outstanding = financial_data.get('shares_outstanding', 0)  # in Cr
            current_price = financial_data.get('current_price', 0)
            
            # Calculate initial FCF if not available
            if fcf <= 0:
                operating_cf = financial_data.get('operating_cash_flow', 0)
                capex = financial_data.get('capital_expenditure', 0)
                fcf = max(operating_cf - capex, revenue * 0.05)  # Fallback to 5% of revenue
            
            # Determine growth rates based on company maturity and sector
            growth_rates = self._determine_growth_rates(financial_data)
            
            # Project future free cash flows
            projected_fcfs = self._project_free_cash_flows(fcf, growth_rates)
            
            # Calculate present value of projected FCFs
            pv_fcfs = self._calculate_present_values(projected_fcfs)
            
            # Calculate terminal value
            terminal_fcf = projected_fcfs[-1] * (1 + self.terminal_growth_rate)
            terminal_value = terminal_fcf / (self.discount_rate - self.terminal_growth_rate)
            pv_terminal = terminal_value / ((1 + self.discount_rate) ** len(projected_fcfs))
            
            # Calculate enterprise value and equity value
            enterprise_value = sum(pv_fcfs) + pv_terminal
            
            # Adjust for net cash/debt
            net_debt = financial_data.get('total_debt', 0) - financial_data.get('cash_and_equivalents', 0)
            equity_value = enterprise_value - net_debt
            
            # Calculate intrinsic value per share
            if shares_outstanding > 0:
                intrinsic_value = equity_value / (shares_outstanding * 10)  # Convert Cr to individual shares
            else:
                intrinsic_value = 0
            
            # Calculate margin of safety and recommendation
            margin_of_safety = self._calculate_margin_of_safety(intrinsic_value, current_price)
            recommendation = self._get_investment_recommendation(margin_of_safety, financial_data)
            
            return {
                'initial_fcf': fcf,
                'growth_rates': growth_rates,
                'projected_fcfs': projected_fcfs,
                'present_value_fcfs': pv_fcfs,
                'terminal_value': terminal_value,
                'pv_terminal_value': pv_terminal,
                'enterprise_value': enterprise_value,
                'net_debt': net_debt,
                'equity_value': equity_value,
                'shares_outstanding': shares_outstanding,
                'intrinsic_value_per_share': intrinsic_value,
                'current_price': current_price,
                'margin_of_safety': margin_of_safety,
                'recommendation': recommendation['action'],
                'confidence': recommendation['confidence'],
                'upside_potential': recommendation['upside'],
                'target_buy_price': intrinsic_value * 0.7,  # 30% margin of safety
                'target_sell_price': intrinsic_value * 1.2,  # 20% upside
                'discount_rate': self.discount_rate,
                'terminal_growth_rate': self.terminal_growth_rate
            }
            
        except Exception as e:
            logger.error(f"DCF calculation failed: {str(e)}")
            return self._get_fallback_dcf_result(financial_data)
    
    def _determine_growth_rates(self, financial_data: Dict[str, Any]) -> List[float]:
        """
        Determine growth rates based on company characteristics
        
        Args:
            financial_data: Financial data dictionary
            
        Returns:
            List of growth rates for projection years
        """
        # Get historical growth rate
        historical_growth = financial_data.get('revenue_growth_3yr', 5.0) / 100
        fcf_growth = financial_data.get('fcf_growth_3yr', historical_growth * 100) / 100
        
        # Use FCF growth if available, otherwise revenue growth
        base_growth = fcf_growth if abs(fcf_growth) > 0.01 else historical_growth
        
        # Cap growth rates based on company size and maturity
        revenue = financial_data.get('revenue', 10000)
        
        if revenue > 50000:  # Large companies (>50k Cr revenue)
            max_growth = min(base_growth * 1.2, 0.15)  # Max 15%
        elif revenue > 20000:  # Medium companies
            max_growth = min(base_growth * 1.5, 0.20)  # Max 20%
        else:  # Smaller companies
            max_growth = min(base_growth * 2.0, 0.25)  # Max 25%
        
        # Ensure minimum reasonable growth
        max_growth = max(max_growth, 0.05)  # Minimum 5%
        
        # 5-year projection with declining growth
        year1_growth = max_growth
        year2_growth = max_growth * 0.8
        year3_growth = max_growth * 0.6
        year4_growth = max_growth * 0.4
        year5_growth = max_growth * 0.3
        
        return [year1_growth, year2_growth, year3_growth, year4_growth, year5_growth]
    
    def _project_free_cash_flows(self, initial_fcf: float, growth_rates: List[float]) -> List[float]:
        """
        Project future free cash flows
        
        Args:
            initial_fcf: Starting free cash flow
            growth_rates: List of growth rates for each year
            
        Returns:
            List of projected FCFs
        """
        projected_fcfs = []
        current_fcf = initial_fcf
        
        for growth_rate in growth_rates:
            current_fcf = current_fcf * (1 + growth_rate)
            projected_fcfs.append(current_fcf)
        
        return projected_fcfs
    
    def _calculate_present_values(self, future_cash_flows: List[float]) -> List[float]:
        """
        Calculate present values of future cash flows
        
        Args:
            future_cash_flows: List of future cash flows
            
        Returns:
            List of present values
        """
        present_values = []
        
        for year, fcf in enumerate(future_cash_flows, 1):
            pv = fcf / ((1 + self.discount_rate) ** year)
            present_values.append(pv)
        
        return present_values
    
    def _calculate_margin_of_safety(self, intrinsic_value: float, current_price: float) -> float:
        """
        Calculate margin of safety
        
        Args:
            intrinsic_value: Calculated intrinsic value
            current_price: Current market price
            
        Returns:
            Margin of safety percentage
        """
        if current_price <= 0:
            return 0.0
        
        return ((intrinsic_value - current_price) / current_price) * 100
    
    def _get_investment_recommendation(self, margin_of_safety: float, 
                                     financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate investment recommendation based on margin of safety and other factors
        
        Args:
            margin_of_safety: Calculated margin of safety
            financial_data: Company financial data
            
        Returns:
            Dictionary with recommendation details
        """
        # Quality factors
        roe = financial_data.get('roe', 0)
        debt_to_equity = financial_data.get('debt_to_equity', 0)
        revenue_growth = financial_data.get('revenue_growth_3yr', 0)
        
        # Base recommendation on margin of safety
        if margin_of_safety > 30:  # > 30% undervalued
            action = "STRONG BUY"
            confidence = "HIGH"
        elif margin_of_safety > 15:  # 15-30% undervalued
            action = "BUY"
            confidence = "HIGH"
        elif margin_of_safety > 0:  # 0-15% undervalued
            action = "BUY"
            confidence = "MEDIUM"
        elif margin_of_safety > -15:  # 0-15% overvalued
            action = "HOLD"
            confidence = "MEDIUM"
        elif margin_of_safety > -30:  # 15-30% overvalued
            action = "AVOID"
            confidence = "MEDIUM"
        else:  # > 30% overvalued
            action = "STRONG AVOID"
            confidence = "HIGH"
        
        # Adjust for quality factors
        quality_score = 0
        if roe > 15:
            quality_score += 1
        if debt_to_equity < 0.5:
            quality_score += 1
        if revenue_growth > 5:
            quality_score += 1
        
        # Upgrade confidence for high-quality companies
        if quality_score >= 2 and action in ["BUY", "STRONG BUY"]:
            confidence = "HIGH"
        elif quality_score <= 1 and action in ["AVOID", "STRONG AVOID"]:
            confidence = "HIGH"
        
        return {
            'action': action,
            'confidence': confidence,
            'upside': margin_of_safety,
            'quality_score': quality_score
        }
    
    def _get_fallback_dcf_result(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide fallback DCF result when calculation fails
        
        Args:
            financial_data: Financial data dictionary
            
        Returns:
            Basic DCF result structure
        """
        current_price = financial_data.get('current_price', 0)
        
        return {
            'initial_fcf': 0,
            'growth_rates': [0.15, 0.12, 0.10, 0.08, 0.05],
            'projected_fcfs': [0, 0, 0, 0, 0],
            'present_value_fcfs': [0, 0, 0, 0, 0],
            'terminal_value': 0,
            'pv_terminal_value': 0,
            'enterprise_value': 0,
            'net_debt': 0,
            'equity_value': 0,
            'shares_outstanding': financial_data.get('shares_outstanding', 0),
            'intrinsic_value_per_share': current_price * 0.7 if current_price > 0 else 100,
            'current_price': current_price,
            'margin_of_safety': -30.0,
            'recommendation': 'HOLD',
            'confidence': 'LOW',
            'upside_potential': -30.0,
            'target_buy_price': current_price * 0.5 if current_price > 0 else 70,
            'target_sell_price': current_price * 1.2 if current_price > 0 else 120,
            'discount_rate': self.discount_rate,
            'terminal_growth_rate': self.terminal_growth_rate
        }


class RelativeValuation:
    """
    Relative Valuation Analysis using multiples
    """
    
    def __init__(self):
        self.industry_multiples = {
            'technology': {'pe': 25, 'pb': 3.5, 'ps': 5.0},
            'banking': {'pe': 15, 'pb': 1.5, 'ps': 3.0},
            'fmcg': {'pe': 30, 'pb': 8.0, 'ps': 4.0},
            'pharmaceutical': {'pe': 20, 'pb': 3.0, 'ps': 6.0},
            'automotive': {'pe': 18, 'pb': 2.0, 'ps': 1.5},
            'default': {'pe': 20, 'pb': 2.5, 'ps': 3.0}
        }
    
    def analyze_relative_valuation(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform relative valuation analysis
        
        Args:
            financial_data: Company financial data
            
        Returns:
            Relative valuation analysis results
        """
        try:
            # Calculate current multiples
            current_multiples = self._calculate_current_multiples(financial_data)
            
            # Get industry benchmarks
            sector = financial_data.get('sector', 'default').lower()
            industry_benchmarks = self.industry_multiples.get(sector, self.industry_multiples['default'])
            
            # Compare with industry
            valuation_scores = self._compare_with_industry(current_multiples, industry_benchmarks)
            
            # Generate relative valuation recommendation
            relative_recommendation = self._get_relative_recommendation(valuation_scores)
            
            return {
                'current_multiples': current_multiples,
                'industry_benchmarks': industry_benchmarks,
                'valuation_scores': valuation_scores,
                'relative_recommendation': relative_recommendation,
                'sector': sector
            }
            
        except Exception as e:
            logger.error(f"Relative valuation analysis failed: {str(e)}")
            return {
                'current_multiples': {},
                'industry_benchmarks': {},
                'valuation_scores': {},
                'relative_recommendation': 'HOLD',
                'sector': 'unknown'
            }
    
    def _calculate_current_multiples(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate current valuation multiples"""
        current_price = financial_data.get('current_price', 0)
        eps = financial_data.get('eps', 0)
        book_value = financial_data.get('book_value_per_share', 0)
        revenue_per_share = financial_data.get('revenue', 0) / financial_data.get('shares_outstanding', 1)
        
        multiples = {}
        
        if eps > 0:
            multiples['pe'] = current_price / eps
        else:
            multiples['pe'] = 0
            
        if book_value > 0:
            multiples['pb'] = current_price / book_value
        else:
            multiples['pb'] = 0
            
        if revenue_per_share > 0:
            multiples['ps'] = current_price / revenue_per_share
        else:
            multiples['ps'] = 0
        
        return multiples
    
    def _compare_with_industry(self, current: Dict[str, float], 
                              industry: Dict[str, float]) -> Dict[str, str]:
        """Compare current multiples with industry benchmarks"""
        scores = {}
        
        for metric in ['pe', 'pb', 'ps']:
            current_val = current.get(metric, 0)
            industry_val = industry.get(metric, 0)
            
            if current_val <= 0 or industry_val <= 0:
                scores[metric] = 'N/A'
            elif current_val < industry_val * 0.8:
                scores[metric] = 'UNDERVALUED'
            elif current_val < industry_val * 1.2:
                scores[metric] = 'FAIRLY_VALUED'
            else:
                scores[metric] = 'OVERVALUED'
        
        return scores
    
    def _get_relative_recommendation(self, scores: Dict[str, str]) -> str:
        """Generate recommendation based on relative valuation scores"""
        undervalued_count = sum(1 for score in scores.values() if score == 'UNDERVALUED')
        overvalued_count = sum(1 for score in scores.values() if score == 'OVERVALUED')
        
        if undervalued_count >= 2:
            return 'BUY'
        elif overvalued_count >= 2:
            return 'AVOID'
        else:
            return 'HOLD'


# Alias for backward compatibility
MultipleValuation = RelativeValuation


def create_dcf_analyzer(discount_rate: float = 0.12, terminal_growth_rate: float = 0.02) -> DCFAnalyzer:
    """
    Create a DCF Analyzer instance
    
    Args:
        discount_rate: WACC or required rate of return (default 12%)
        terminal_growth_rate: Long-term growth rate (default 2%)
        
    Returns:
        DCFAnalyzer instance
    """
    return DCFAnalyzer(discount_rate, terminal_growth_rate)


class RiskAssessment:
    """
    Risk Assessment and Analysis
    """
    
    def assess_investment_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess investment risk based on financial metrics
        
        Args:
            financial_data: Company financial data
            
        Returns:
            Risk assessment results
        """
        try:
            # Financial risk factors
            debt_risk = self._assess_debt_risk(financial_data)
            liquidity_risk = self._assess_liquidity_risk(financial_data)
            profitability_risk = self._assess_profitability_risk(financial_data)
            growth_risk = self._assess_growth_risk(financial_data)
            
            # Overall risk score
            risk_factors = [debt_risk, liquidity_risk, profitability_risk, growth_risk]
            overall_risk = self._calculate_overall_risk(risk_factors)
            
            return {
                'debt_risk': debt_risk,
                'liquidity_risk': liquidity_risk,
                'profitability_risk': profitability_risk,
                'growth_risk': growth_risk,
                'overall_risk': overall_risk,
                'risk_rating': self._get_risk_rating(overall_risk)
            }
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            return {
                'debt_risk': 'MEDIUM',
                'liquidity_risk': 'MEDIUM',
                'profitability_risk': 'MEDIUM',
                'growth_risk': 'MEDIUM',
                'overall_risk': 50.0,
                'risk_rating': 'MEDIUM'
            }
    
    def _assess_debt_risk(self, financial_data: Dict[str, Any]) -> str:
        """Assess debt-related risk"""
        debt_to_equity = financial_data.get('debt_to_equity', 0)
        
        if debt_to_equity < 0.3:
            return 'LOW'
        elif debt_to_equity < 0.7:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _assess_liquidity_risk(self, financial_data: Dict[str, Any]) -> str:
        """Assess liquidity risk"""
        current_ratio = financial_data.get('current_ratio', 0)
        
        if current_ratio > 2.0:
            return 'LOW'
        elif current_ratio > 1.2:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _assess_profitability_risk(self, financial_data: Dict[str, Any]) -> str:
        """Assess profitability risk"""
        roe = financial_data.get('roe', 0)
        profit_margin = financial_data.get('profit_margin', 0)
        
        if roe > 15 and profit_margin > 10:
            return 'LOW'
        elif roe > 10 and profit_margin > 5:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _assess_growth_risk(self, financial_data: Dict[str, Any]) -> str:
        """Assess growth sustainability risk"""
        revenue_growth = financial_data.get('revenue_growth_3yr', 0)
        
        if revenue_growth > 10:
            return 'LOW'
        elif revenue_growth > 5:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _calculate_overall_risk(self, risk_factors: List[str]) -> float:
        """Calculate overall risk score"""
        risk_scores = {'LOW': 25, 'MEDIUM': 50, 'HIGH': 75}
        total_score = sum(risk_scores.get(risk, 50) for risk in risk_factors)
        return total_score / len(risk_factors)
    
    def _get_risk_rating(self, risk_score: float) -> str:
        """Get risk rating based on score"""
        if risk_score < 35:
            return 'LOW'
        elif risk_score < 65:
            return 'MEDIUM'
        else:
            return 'HIGH'
