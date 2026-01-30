# tests/graph/nodes/test_decision_node_with_history.py

from unittest.mock import MagicMock, patch
from types import SimpleNamespace

from app.graph.nodes.decision import decision_node


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

class FakeResponse:
    def __init__(self, content: str):
        self.content = content


def make_state(
    *,
    question="Should we migrate to LangGraph?",
    analysis="Analysis content",
    rag_context="",
    historical_evidence=None,
):
    return {
        "question": question,
        "analysis": analysis,
        "rag_context": rag_context,
        "historical_evidence": historical_evidence or [],
    }


# ------------------------------------------------------------------
# Test
# ------------------------------------------------------------------

@patch(
    "app.graph.nodes.decision.DecisionPromptBuilder.build"
)
@patch(
    "app.graph.nodes.decision.historical_confidence_factor"
)
def test_decision_node_uses_historical_confidence(
    mock_historical_factor,
    mock_prompt_builder,
):
    # --------------------------------------------------------------
    # Arrange
    # --------------------------------------------------------------

    # Fake prompt bundle
    mock_prompt_builder.return_value = SimpleNamespace(
        system_message=SimpleNamespace(content="SYSTEM PROMPT"),
        human_message=SimpleNamespace(content="HUMAN PROMPT"),
        rag_significant=False,
        rag_mode="NONE"
    )

    # Historical confidence factor returns +0.1
    mock_historical_factor.return_value = 0.10

    # Fake LLM
    fake_llm = MagicMock()
    fake_llm.invoke.return_value = FakeResponse(
        "Decision: YES\nConfidence: 0.9"
    )

    state = make_state(
        historical_evidence=[
            {"similarity_score": 0.85, "confidence": 0.8}
        ]
    )

    # --------------------------------------------------------------
    # Act
    # --------------------------------------------------------------

    result = decision_node(state, llm=fake_llm)

    # --------------------------------------------------------------
    # Assert
    # --------------------------------------------------------------

    assert result["decision"] == "YES"
    assert result["confidence"] == 1.0  # 0.9 + 0.1 capped
    assert "messages" in result
    assert len(result["messages"]) == 1

    # Ensure historical factor was applied
    mock_historical_factor.assert_called_once_with(
        state["historical_evidence"]
    )

    # Ensure LLM was used
    fake_llm.invoke.assert_called_once()
