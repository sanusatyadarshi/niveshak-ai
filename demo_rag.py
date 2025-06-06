#!/usr/bin/env python3
"""
Simple demonstration of the working NiveshakAI RAG pipeline.
"""
import os
import sys
import yaml
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

from src.analysis.query import QueryEngine

def demo_rag_pipeline():
    """Demonstrate the working RAG pipeline with Philip Fisher's knowledge."""
    print("🚀 NiveshakAI RAG Pipeline Demonstration")
    print("=" * 50)
    
    # Initialize the query engine
    print("📚 Initializing query engine...")
    query_engine = QueryEngine('config/settings.yaml')
    print("✅ Query engine initialized with DeepSeek R1 and Philip Fisher's knowledge base")
    
    # Demo queries about Philip Fisher's investment principles
    demo_queries = [
        "What are the key characteristics of a growth stock according to Philip Fisher?",
        "How does Fisher recommend evaluating management quality?",
        "What is Fisher's scuttlebutt method?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🤔 Query {i}: {query}")
        print("-" * 60)
        
        try:
            # Process the query
            print("🔍 Searching knowledge base...")
            response = query_engine.process_query(query)
            
            print(f"📖 Found {len(response.sources)} relevant sources from Philip Fisher's book")
            print(f"\n💡 AI Analysis:")
            print(response.answer[:300] + "..." if len(response.answer) > 300 else response.answer)
            
            if response.sources:
                print("\nSource Excerpts:")
                for source in response.sources:
                    print(source)
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    demo_rag_pipeline()
