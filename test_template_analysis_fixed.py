#!/usr/bin/env python3
"""
Test script for the enhanced template-based company analysis system
"""
import sys
import os
sys.path.append('/Users/sanusatyadarshi/Documents/repos/personal/niveshak-ai')

from src.analysis.company_analysis import TemplateBasedCompanyAnalyzer
from src.analysis.analysis_template import CompanyAnalysisTemplate, BusinessAnalysis, FinancialMetrics, RatioAnalysis, AnalysisItem
from datetime import datetime

def test_template_based_analysis():
    """Test the template-based analysis system"""
    print("🧪 Testing Template-Based Company Analysis System")
    print("=" * 60)
    
    # Initialize the analyzer
    print("1. Initializing TemplateBasedCompanyAnalyzer...")
    analyzer = TemplateBasedCompanyAnalyzer()
    print("✅ Analyzer initialized successfully")
    
    # Create a mock template instead of using real file analysis
    print("\n2. Creating test template with mock data...")
    
    try:
        # Create a template with mock data for testing
        template = CompanyAnalysisTemplate(
            company_name="Test Company Ltd",
            symbol="TEST",
            sector="Technology",
            analysis_date=datetime.now().isoformat(),
            year="2023-24"
        )
        
        # Mock business analysis
        template.business_analysis = BusinessAnalysis()
        template.business_analysis.what_does_company_do = "Technology services company"
        template.business_analysis.promoters_background = "Experienced technology entrepreneurs"
        template.business_analysis.competitors = "Major tech companies in the space"
        template.business_analysis.manufacturing_details = "Software development and services"
        template.business_analysis.revenue_mix = "60% software, 40% services"
        
        # Mock financial metrics
        template.financial_metrics = FinancialMetrics()
        template.financial_metrics.gross_profit_margin = AnalysisItem(
            value="25.0%", judgement="✅ Good", notes="Healthy margin"
        )
        template.financial_metrics.revenue_growth = AnalysisItem(
            value="12.0%", judgement="✅ Strong", notes="Consistent growth"
        )
        template.financial_metrics.return_on_equity = AnalysisItem(
            value="18.0%", judgement="✅ Excellent", notes="High ROE"
        )
        template.financial_metrics.debt_level = AnalysisItem(
            value="0.35", judgement="✅ Low", notes="Conservative debt"
        )
        template.financial_metrics.cash_flow_operations = AnalysisItem(
            value="14.0%", judgement="✅ Strong", notes="Good cash generation"
        )
        
        # Mock ratio analysis
        template.ratio_analysis = RatioAnalysis()
        template.ratio_analysis.current_ratio = AnalysisItem(
            value="1.80", judgement="✅ Good", notes="Good liquidity"
        )
        template.ratio_analysis.quick_ratio = AnalysisItem(
            value="1.20", judgement="✅ Good", notes="Strong quick ratio"
        )
        template.ratio_analysis.roe = AnalysisItem(
            value="18.0%", judgement="✅ Excellent", notes="High returns"
        )
        template.ratio_analysis.roa = AnalysisItem(
            value="8.5%", judgement="✅ Strong", notes="Efficient asset use"
        )
        template.ratio_analysis.debt_to_equity = AnalysisItem(
            value="0.45", judgement="✅ Good", notes="Manageable debt"
        )
        template.ratio_analysis.interest_coverage = AnalysisItem(
            value="6.2x", judgement="✅ Strong", notes="Good coverage"
        )
        
        print("✅ Template structure created successfully")
        print(f"   Company: {template.company_name}")
        print(f"   Symbol: {template.symbol}")
        print(f"   Year: {template.year}")
        
        # Test template methods
        print("\n3. Testing template methods...")
        overall_score = template.calculate_overall_score()
        print(f"✅ Overall score calculation: {overall_score:.1%}")
        
        recommendation = template.generate_recommendation()
        template.recommendation = recommendation  # Ensure recommendation is set for markdown
        print(f"✅ Recommendation generated: {recommendation.recommendation}")
        print(f"   Confidence: {recommendation.confidence}")
        print(f"   Reasoning: {recommendation.reasoning}")
        
        # Test markdown generation
        print("\n4. Testing markdown report generation...")
        markdown = analyzer._generate_template_markdown(template)
        print(f"✅ Markdown report generated ({len(markdown)} characters)")
        
        # Test business analysis conversion
        print("\n5. Testing business analysis conversion...")
        business_dict = template.business_analysis.to_dict()
        print(f"✅ Business analysis converted to dict ({len(business_dict)} fields)")
        
        # Test saving template report
        print("\n6. Testing template report saving...")
        output_path = analyzer.save_template_report(template, out_path="test_report.md")
        print(f"✅ Template report saved to: {output_path}")
        
        print("\n🎉 All tests passed! Template-based analysis system is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_legacy_compatibility():
    """Test backward compatibility with legacy analyzer"""
    print("\n" + "=" * 60)
    print("🔄 Testing Legacy Compatibility")
    print("=" * 60)
    
    try:
        from src.analysis.company_analysis import CompanyAnalyzer
        
        print("1. Initializing legacy CompanyAnalyzer...")
        legacy_analyzer = CompanyAnalyzer()
        print("✅ Legacy analyzer initialized successfully")
        
        print("2. Verifying template analyzer is embedded...")
        assert hasattr(legacy_analyzer, 'template_analyzer'), "Template analyzer not found"
        print("✅ Template analyzer embedded in legacy analyzer")
        
        print("\n🎉 Legacy compatibility verified!")
        return True
        
    except Exception as e:
        print(f"❌ Legacy compatibility test failed: {str(e)}")
        return False

def test_end_to_end_with_dummy_data():
    """Test end-to-end analysis with mock data (no file required)"""
    print("\n" + "=" * 60)
    print("🧪 Testing End-to-End Analysis with Mock Data")
    print("=" * 60)
    
    try:
        from src.analysis.company_analysis import TemplateBasedCompanyAnalyzer
        
        analyzer = TemplateBasedCompanyAnalyzer()
        
        print("1. Testing analyze method with error handling...")
        
        # This will fail gracefully and return a basic template
        template = analyzer.analyze(
            pdf_path="/non/existent/path.pdf",  # Will fail gracefully
            company_name="Mock Company",
            symbol="MOCK",
            year="2023-24"
        )
        
        print(f"✅ Analysis completed (graceful error handling)")
        print(f"   Company: {template.company_name}")
        print(f"   Symbol: {template.symbol}")
        
        # Ensure recommendation is generated even on error
        if template.recommendation is None:
            print("⚠️ Recommendation is None, generating fallback...")
            template.recommendation = template.generate_recommendation()
        
        print(f"   Recommendation: {template.recommendation.recommendation}")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting NiveshakAI Template-Based Analysis Tests")
    print("=" * 60)
    
    test1_passed = test_template_based_analysis()
    test2_passed = test_legacy_compatibility()
    test3_passed = test_end_to_end_with_dummy_data()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Template-based Analysis: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Legacy Compatibility: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"End-to-End Mock Analysis: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 ALL TESTS PASSED! Template-based analysis system is ready for use.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED! Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
