#!/usr/bin/env python
# Quick test script to verify the graph works

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.graph.graph import compiled_graph
from app.graph.state import DecisionState

def test_graph():
    print("🧪 Testing AI Decision Agent Graph...")
    print("=" * 60)
    
    # Check if API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set!")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        return False
    
    print("✅ OPENAI_API_KEY is set")
    
    # Create test state
    state = DecisionState(
        messages=[],
        question="Should a small startup use LangGraph?",
        plan=None,
        retrieved_docs=[],
        analysis=None,
        decision=None,
        confidence=None,
        attempts=0
    )
    
    # Configure with thread_id
    config = {
        "configurable": {
            "thread_id": "test_thread_123"
        }
    }
    
    print("\n📝 Test question: 'Should a small startup use LangGraph?'")
    print("\n🔄 Running graph...")
    
    try:
        result = compiled_graph.invoke(state, config=config)
        
        print("\n" + "=" * 60)
        print("✅ Graph execution successful!")
        print("=" * 60)
        
        print(f"\n📋 Plan:\n{result.get('plan', 'N/A')[:200]}...")
        print(f"\n🔍 Analysis:\n{result.get('analysis', 'N/A')[:200]}...")
        print(f"\n⚖️  Decision:\n{result.get('decision', 'N/A')[:200]}...")
        print(f"\n📊 Confidence: {result.get('confidence', 'N/A')}")
        print(f"\n🔁 Attempts: {result.get('attempts', 0)}")
        print(f"\n💬 Messages: {len(result.get('messages', []))}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_graph()
    sys.exit(0 if success else 1)

