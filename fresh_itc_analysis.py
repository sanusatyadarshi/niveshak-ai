#!/usr/bin/env python3
"""
Fresh ITC Analysis using the main NiveshakAI workflow

This script demonstrates the complete analysis workflow with:
1. Current price input from user
2. Multi-year financial data extraction
3. DCF valuation based on 3-year historical data
4. Comprehensive analysis report generation
"""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

def run_fresh_itc_analysis():
    """Run a fresh ITC analysis using the main workflow"""
    print("🏭 Fresh ITC Analysis - NiveshakAI")
    print("=" * 50)
    
    try:
        from analysis.symbol_stock_analyzer import SymbolStockAnalyzer
        
        # Initialize the analyzer
        analyzer = SymbolStockAnalyzer()
        print("✅ Initialized SymbolStockAnalyzer")
        
        # Check if ITC annual reports exist
        itc_dir = project_root / 'data' / 'annual_reports' / 'ITC'
        if not itc_dir.exists() or len(list(itc_dir.glob("*.pdf"))) == 0:
            print(f"❌ No ITC annual reports found in {itc_dir}")
            print("📁 Please ensure annual reports are available in:")
            print(f"   {itc_dir}/2023.pdf")
            print(f"   {itc_dir}/2024.pdf") 
            print(f"   {itc_dir}/2025.pdf")
            return None
        
        # Find latest PDF
        pdf_files = list(itc_dir.glob("*.pdf"))
        latest_pdf = max(pdf_files, key=lambda x: x.stem)
        
        print(f"📁 Found {len(pdf_files)} ITC annual reports")
        print(f"📊 Using latest report: {latest_pdf.name}")
        
        # Run the analysis (this will prompt for current price)
        print(f"\n🔄 Starting comprehensive analysis...")
        result = analyzer.analyze_symbol("ITC", str(latest_pdf))
        
        if result:
            print(f"\n✅ Fresh ITC analysis completed!")
            print(f"📄 Report generated: {result}")
            return result
        else:
            print(f"\n❌ Analysis failed")
            return None
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🧮 NiveshakAI - Fresh ITC Stock Analysis")
    print("Using production workflow with enhanced multi-year DCF")
    print()
    
    result = run_fresh_itc_analysis()
    
    if result:
        print("\n" + "=" * 50)
        print("✅ Fresh analysis completed successfully!")
        print(f"📄 New report available at: {result}")
        print("\n📊 Analysis includes:")
        print("   • Current market price validation")
        print("   • 3-year historical financial data")
        print("   • DCF valuation with realistic assumptions")
        print("   • Investment recommendation")
        print("   • Risk assessment and price targets")
    else:
        print("\n" + "=" * 50)
        print("❌ Analysis failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
