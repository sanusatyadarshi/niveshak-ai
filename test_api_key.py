#!/usr/bin/env python3
"""Test the OpenAI API key loading"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_env_loading():
    """Test environment variable loading"""
    print("🧪 Testing environment variable loading...")
    
    # Test 1: Direct environment access
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"Direct env access: {'✅ Found' if api_key else '❌ Not found'}")
    if api_key:
        print(f"   Key preview: {api_key[:20]}...")
    
    # Test 2: With dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key_dotenv = os.getenv('OPENAI_API_KEY')
        print(f"After dotenv load: {'✅ Found' if api_key_dotenv else '❌ Not found'}")
        if api_key_dotenv:
            print(f"   Key preview: {api_key_dotenv[:20]}...")
    except ImportError:
        print("❌ python-dotenv not available")
    
    # Test 3: LLMPDFAnalyzer initialization
    try:
        from analysis.llm_pdf_analyzer import LLMPDFAnalyzer
        print("🤖 Testing LLMPDFAnalyzer initialization...")
        analyzer = LLMPDFAnalyzer()
        print("✅ LLMPDFAnalyzer initialized successfully")
    except Exception as e:
        print(f"❌ LLMPDFAnalyzer failed: {e}")
    
    # Test 4: QueryEngine initialization
    try:
        from analysis.query import QueryEngine
        print("🤖 Testing QueryEngine initialization...")
        engine = QueryEngine()
        print("✅ QueryEngine initialized successfully")
    except Exception as e:
        print(f"❌ QueryEngine failed: {e}")

if __name__ == "__main__":
    test_env_loading()
