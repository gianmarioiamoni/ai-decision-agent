# app/graph/nodes/router.py
# Routing logic for decision flow (STEP 0.3 compliant)
# This node does NOT mutate state.
# It only decides the next transition label.

from app.graph.state import DecisionState


# Minimum confidence threshold for accepting a decision (0 to 1)
MIN_CONFIDENCE = 0.70


def should_retry(state: DecisionState) -> str:
    """
    Determines whether the workflow should retry analysis/retrieval
    or proceed to finalization.

    Returns:
    - "retry" → graph should loop back (retrieval / analysis)
    - "end"   → graph should proceed to finalization
    """

    if state.confidence_final is None:
        # No confidence computed yet → retry
        print("⚠️ No confidence score available - retrying")
        return "retry"

    if state.confidence_final >= MIN_CONFIDENCE:
        # Sufficient confidence → finalize
        print(
            f"✅ Confidence {state.confidence_final:.2f} "
            f">= threshold {MIN_CONFIDENCE:.2f} - finalizing"
        )
        return "end"

    # Low confidence case
    print(
        f"🔄 Low confidence ({state.confidence_final:.2f}) "
        f"< threshold {MIN_CONFIDENCE:.2f}"
    )

    # If analysis explicitly signals uncertainty, retry may help
    if state.analysis and any(
        keyword in state.analysis.lower()
        for keyword in ["assumption", "unclear", "uncertain"]
    ):
        print("   → Retry suggested due to uncertainty in analysis")
        return "retry"

    # Default: accept low-confidence decision to avoid infinite loops
    print("   → End: accepting low-confidence decision")
    return "end"

