#!/usr/bin/env python3
"""
Generic Stock Analysis Script for NiveshakAI
Analyzes any NSE/BSE stock using the SymbolStockAnalyzer
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analysis.symbol_stock_analyzer import SymbolStockAnalyzer

def main():
    print("🚀 NiveshakAI - Stock Analysis System")
    print("=" * 50)
    
    # Get stock symbol and price from user
    symbol = input("Enter stock symbol (e.g., RELIANCE, TCS, ITC): ").strip().upper()
    
    while True:
        try:
            current_price = float(input(f"Enter current price for {symbol}: ₹"))
            break
        except ValueError:
            print("Please enter a valid price (numbers only)")
    
    print(f"\n📊 Analyzing {symbol} at ₹{current_price:.2f}...")
    print("-" * 40)
    
    try:
        # Initialize the analyzer
        analyzer = SymbolStockAnalyzer()
        
        # Run the analysis
        result = analyzer.analyze_symbol(symbol, current_price)
        
        if result:  # Check if result is not empty
            print(f"✅ Analysis completed successfully!")
            print(f"📄 Report generated: {result['report_path']}")
            print(f"💰 Intrinsic Value: ₹{result['intrinsic_value']:.2f}")
            print(f"📈 Current Price: ₹{current_price:.2f}")
            
            # Calculate recommendation
            if current_price <= result['intrinsic_value']:
                recommendation = "🟢 BUY - Stock appears undervalued"
            else:
                recommendation = "🔴 AVOID - Stock appears overvalued"
            
            print(f"💡 Recommendation: {recommendation}")
            
        else:
            print(f"❌ Analysis failed - please check the logs for details")
            
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()
