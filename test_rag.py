#!/usr/bin/env python3
"""
RAG Pipeline Integration Test
Validates the complete RAG (Retrieval Augmented Generation) pipeline
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import yaml
import ollama

# Add src to path for import
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Load environment variables
load_dotenv()

from src.embedding.embedder import EmbeddingManager
from src.analysis.query import QueryEngine

def test_ollama_connection():
    """Test basic Ollama connection."""
    print("🔄 Testing Ollama connection...")
    try:
        models = ollama.list()
        print(f"✅ Ollama connected. Available models: {len(models['models'])}")
        for model in models['models']:
            model_name = model.get('name', 'Unknown')
            print(f"   - {model_name}")
        return True
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def test_simple_llm_call():
    """Test a simple LLM call."""
    print("\n🔄 Testing simple LLM call...")
    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[{'role': 'user', 'content': 'What is 2+2? Answer briefly.'}],
            options={'temperature': 0.1, 'num_predict': 50}
        )
        result = response['message']['content']
        print(f"✅ LLM response: {result[:100]}...")
        return True
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return False

def test_vector_search():
    """Test vector search functionality."""
    print("\n🔄 Testing vector search...")
    try:
        # Load config
        with open('config/settings.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize embedding manager
        embedding_manager = EmbeddingManager(config)
        
        # Test search
        results = embedding_manager.search_knowledge_base("Philip Fisher growth stocks", top_k=3)
        print(f"✅ Vector search returned {len(results)} results")
        
        if results:
            content, metadata, score = results[0]  # Unpack the tuple
            print(f"   First result: {content[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Vector search failed: {e}")
        return False

def test_full_pipeline():
    """Test the full RAG pipeline with a simple query."""
    print("\n🔄 Testing full RAG pipeline...")
    try:
        # Temporarily update config to use smaller model
        config_path = 'config/settings.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update to use smaller model
        original_model = config['api']['ollama']['model']
        config['api']['ollama']['model'] = 'llama3.2:3b'
        config['api']['ollama']['max_tokens'] = 200  # Shorter response
        
        # Write temporary config
        with open(config_path + '.temp', 'w') as f:
            yaml.safe_dump(config, f)
        
        # Initialize query engine
        query_engine = QueryEngine(config_path + '.temp')
        
        # Test query
        response = query_engine.process_query("What is fundamental analysis? Answer briefly.")
        
        print(f"✅ Full pipeline successful!")
        print(f"   Query: What is fundamental analysis?")
        print(f"   Response: {response.answer[:150]}...")
        print(f"   Sources: {len(response.sources)} documents")
        
        # Cleanup
        os.remove(config_path + '.temp')
        
        # Restore original config
        config['api']['ollama']['model'] = original_model
        with open(config_path, 'w') as f:
            yaml.safe_dump(config, f)
        
        return True
    except Exception as e:
        print(f"❌ Full pipeline failed: {e}")
        
        # Cleanup on error
        if os.path.exists(config_path + '.temp'):
            os.remove(config_path + '.temp')
        
        return False

if __name__ == "__main__":
    print("🚀 NiveshakAI RAG Pipeline Test\n")
    
    # Run tests
    tests = [
        test_ollama_connection,
        test_simple_llm_call,
        test_vector_search,
        test_full_pipeline
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! RAG pipeline is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
