#!/usr/bin/env python3
"""Test environment variable loading"""

import os
print("Testing environment variable loading...")

# Test 1: Check if OPENAI_API_KEY is set
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"✅ OPENAI_API_KEY found: {api_key[:20]}...")
else:
    print("❌ OPENAI_API_KEY not found in environment")

# Test 2: Try loading with dotenv
try:
    from dotenv import load_dotenv
    print("✅ python-dotenv is available")
    
    # Load .env file
    load_dotenv()
    
    # Check again after loading
    api_key_after = os.getenv('OPENAI_API_KEY')
    if api_key_after:
        print(f"✅ OPENAI_API_KEY after dotenv: {api_key_after[:20]}...")
    else:
        print("❌ OPENAI_API_KEY still not found after dotenv")
        
except ImportError:
    print("❌ python-dotenv not available")

# Test 3: Try loading specific .env file
print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")

if os.path.exists('.env'):
    with open('.env', 'r') as f:
        content = f.read()
        print(f".env file content preview: {content[:100]}...")
