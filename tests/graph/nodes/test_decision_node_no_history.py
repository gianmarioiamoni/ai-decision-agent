# tests/graph/nodes/test_decision_node_no_history.py

from app.graph.nodes.decision import decision_node
from app.graph.state import DecisionState


class FakeLLM:
    #
    # Minimal LLM stub for deterministic testing
    #
    def invoke(self, messages):
        class Response:
            content = (
                "Decision: Proceed with the proposed plan.\n"
                "Confidence: 0.75"
            )
        return Response()


def _base_state() -> DecisionState:
    #
    # Minimal valid DecisionState for decision node
    #
    return {
        "messages": [],
        "user_query": "Should we adopt this architecture?",
        "input_context_docs": [],
        "input_metadata": {},
        "context_hash": "test",

        "plan": "Adopt clean layered architecture",

        "authoritative_context": [],
        "general_context": [],
        "query_similarity": [],
        "rag_context": None,

        "analysis": "The architecture improves maintainability.",

        "risks": [],
        "assumptions": [],
        "confidence_base": None,

        "decision": None,
        "justification": None,
        "confidence_final": None,

        "similar_decisions": [],
        "historical_confidence_factor": 1.0,

        "confidence_final_history": [],
        "confidence_drift": None,

        "attempts": 0,
        "needs_retry": False,
        "decision_finalized": False,

        "report_html": None,
        "report_preview": None,

        "errors": [],

        "decision_id": "test-id",
        "timestamp": "2026-01-01T00:00:00Z",

        "history_used": False,
        "confidence_breakdown": {},
    }


def test_decision_node_without_history():
    #
    # GIVEN a valid state without historical evidence
    #
    state = _base_state()
    llm = FakeLLM()

    # WHEN decision node is executed
    result = decision_node(state, llm=llm)

    # THEN decision is produced
    assert result["decision"] is not None
    assert "Proceed" in result["decision"]

    # AND confidence is computed
    assert result["confidence_base"] == 0.75
    assert result["confidence_final"] == 0.75

    # AND no history influence is applied
    assert result["history_used"] is False

    # AND messages are appended
    assert len(result["messages"]) >= 2
