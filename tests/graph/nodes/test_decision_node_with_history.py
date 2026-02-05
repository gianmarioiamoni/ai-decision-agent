# tests/graph/nodes/test_decision_node_with_history.py

from app.graph.nodes.decision import decision_node
from app.graph.state import DecisionState


class FakeLLM:
    #
    # Deterministic LLM stub
    #
    def invoke(self, messages):
        class Response:
            content = (
                "Decision: Proceed with the proposed plan.\n"
                "Confidence: 0.70"
            )
        return Response()


def _base_state() -> DecisionState:
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

        # 🔥 Historical evidence present
        "similar_decisions": [
            {
                "decision": "Proceed with similar architecture",
                "confidence": 0.85,
                "similarity_score": 0.92,
            }
        ],
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

        "history_used": True,
        "confidence_breakdown": {},
    }


def test_decision_node_with_history_increases_confidence():
    #
    # GIVEN a valid state with historical evidence
    #
    state = _base_state()
    llm = FakeLLM()

    # WHEN decision node is executed
    result = decision_node(state, llm=llm)

    # THEN decision is produced
    assert result["decision"] is not None

    # AND base confidence is parsed
    assert result["confidence_base"] == 0.70

    # AND historical evidence increases final confidence
    assert result["confidence_final"] > result["confidence_base"]

    # AND history usage is explicit
    assert result["history_used"] is True
