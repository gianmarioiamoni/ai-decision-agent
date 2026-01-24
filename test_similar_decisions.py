#!/usr/bin/env python3
# Test script to check if similar decisions retrieval is working

import os
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "dummy-key-for-test")

from app.graph.memory import init_chroma_vectorstore, retrieve_similar_decisions

# Initialize Chroma
print("Initializing Chroma vectorstore...")
chroma = init_chroma_vectorstore()

# Test question
test_question = "Should we adopt a new technology for our team?"

print(f"\nTesting retrieval for question: '{test_question}'")
print("="*60)

# Retrieve similar decisions
similar = retrieve_similar_decisions(test_question, chroma, top_k=3)

print("\n" + "="*60)
print(f"RESULT: Found {len(similar)} similar decisions")
if similar:
    for i, sd in enumerate(similar, 1):
        print(f"\n{i}. Decision ID: {sd['decision_id']}")
        print(f"   Similarity: {sd['similarity']:.4f}")
        print(f"   Content: {sd['content'][:200]}...")
else:
    print("\n⚠️ No similar decisions found!")
    print("\nPossible causes:")
    print("- Chroma collection is empty")
    print("- Collection name mismatch")
    print("- Embedding function mismatch")
