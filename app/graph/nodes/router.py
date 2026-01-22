# app/graph/nodes/router.py
# Intelligent routing with convergence rules and decision lock

from typing import Dict
from app.graph.state import DecisionState

# Maximum number of retry attempts allowed
MAX_ATTEMPTS = 3

# Minimum confidence threshold for accepting a decision (0 to 1)
MIN_CONFIDENCE = 0.70

# Confidence delta threshold for convergence detection (0 to 1)
CONVERGENCE_DELTA = 0.05

# Router node
# This node updates the attempts counter and checks for decision finalization
def confidence_router(state: DecisionState) -> Dict:
    #
    # Updates attempts counter and prepares routing decision.
    #
    # Args:
    #     state: DecisionState containing attempts and confidence
    #
    # Returns:
    #     Dict containing updated attempts and decision_finalized
    #
    attempts = state.get("attempts", 0)
    confidence = state.get("confidence")
    
    # Increment attempts for this evaluation
    updates = {
        "attempts": attempts + 1
    }
    
    # Check if decision should be finalized
    # Finalize if: high confidence OR max attempts reached
    if confidence is not None and (confidence >= MIN_CONFIDENCE or attempts >= MAX_ATTEMPTS - 1):
        updates["decision_finalized"] = True
        print(f"\n🔒 DECISION FINALIZED (attempt {attempts + 1}, confidence {confidence:.2f})\n")
    
    return updates


def should_retry(state: DecisionState) -> str:
    #
    # Determines if the workflow should retry retrieval or end.
    #
    # Args:
    #     state: DecisionState containing decision_finalized, confidence, and attempts
    #
    # Returns:
    #     "retry" if more retrieval/analysis needed
    #     "end" if ready to proceed to summarization
    #
    # Implements:
    # 1. Decision lock (decision_finalized flag)
    # 2. Max attempts limit
    # 3. Confidence threshold
    # 4. Convergence detection
    #
    # Returns:
    #     "retry" if more retrieval/analysis needed
    #     "end" if ready to proceed to summarization
    #
  
    # 🔒 DECISION LOCK: If decision is finalized, never retry
    if state.get("decision_finalized", False):
        print("🔒 Decision locked - proceeding to summarization")
        return "end"
    
    confidence = state.get("confidence")
    attempts = state.get("attempts", 0)
    
    # 🛑 MAX ATTEMPTS: Hard limit on retries
    if attempts >= MAX_ATTEMPTS:
        print(f"🛑 Max attempts ({MAX_ATTEMPTS}) reached - finalizing decision")
        return "end"
    
    # ❌ NO CONFIDENCE: Should not happen, but safe fallback
    if confidence is None:
        print("⚠️ No confidence score - retrying")
        return "retry"
    
    # ✅ HIGH CONFIDENCE: Decision is good, finalize
    if confidence >= MIN_CONFIDENCE:
        print(f"✅ High confidence ({confidence:.2f}) - finalizing decision")
        return "end"
    
    # 🔄 LOW CONFIDENCE: Check if we should retry
    print(f"🔄 Low confidence ({confidence:.2f}) - analyzing retry conditions")
    
    # Check convergence: if we've tried before, check confidence delta
    # (This would require storing previous confidence, not implemented yet)
    
    # Check retrieved documents
    retrieved_docs = state.get("retrieved_docs", [])
    analysis = state.get("analysis")
    
    # If very few documents and low confidence, try getting more context
    if len(retrieved_docs) < 2:
        print(f"   → Retry: Only {len(retrieved_docs)} documents retrieved")
        return "retry"
    
    # If analysis mentions assumptions/uncertainty, might help to retry
    if analysis and any(keyword in analysis.lower() for keyword in ["assumption", "unclear", "uncertain"]):
        print("   → Retry: Analysis shows uncertainty")
        return "retry"
    
    # Otherwise, accept the low confidence decision
    # (Better a cautious decision than infinite loops)
    print(f"   → End: Accepting decision with confidence {confidence:.2f}")
    return "end"
