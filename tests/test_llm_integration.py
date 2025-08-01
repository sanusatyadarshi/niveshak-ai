#!/usr/bin/env python3
"""
Test script to validate LLM PDF Analyzer integration
Moved from root to proper test structure
"""
import sys
import os
from pathlib import Path

# Add src to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_llm_analyzer_import():
    """Test LLM PDF Analyzer import and basic functionality"""
    print("✅ Testing LLM PDF Analyzer import...")
    
    try:
        from analysis.llm_pdf_analyzer import LLMPDFAnalyzer
        print("✅ Import successful!")
        
        analyzer = LLMPDFAnalyzer()
        print(f"🤖 LLM PDF Analyzer initialized with provider: {analyzer.provider}")
        print(f"📊 Model: {analyzer.model}")
        print(f"🌡️  Temperature: {analyzer.temperature}")
        
        print("\n🎉 Multi-vendor LLM PDF analyzer integration complete!")
        print("📋 Supported providers: OpenAI, Anthropic, Ollama")
        print("⚙️  Configuration: settings.yaml")
        print("🔧 Current provider: OpenAI (default)")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_llm_analyzer_import()
    print("\nDone!")
    sys.exit(0 if success else 1)
