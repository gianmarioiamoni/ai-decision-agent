# tests/graph/nodes/test_historical_retriever_node.py

import pytest
from unittest.mock import Mock, patch

from app.graph.nodes.historical_retriever import historical_retriever_node


def test_historical_retriever_node_requires_question():
    with pytest.raises(ValueError):
        historical_retriever_node({})


@patch(
    "app.graph.nodes.historical_retriever._get_historical_retriever"
)
def test_historical_retriever_node_returns_evidence_only(mock_get_retriever):
    mock_retriever = Mock()
    mock_retriever.retrieve.return_value = [
        {"decision": "YES", "similarity": 0.9, "confidence": 0.8},
        {"decision": "NO", "similarity": 0.85, "confidence": 0.7},
    ]

    mock_get_retriever.return_value = mock_retriever

    state = {
        "question": "Should we adopt LangGraph?",
        "some_other_state": "do_not_touch",
    }

    result = historical_retriever_node(state)

    assert result == {
        "historical_evidence": mock_retriever.retrieve.return_value
    }

    mock_retriever.retrieve.assert_called_once_with(
        query="Should we adopt LangGraph?",
        k=3,
    )
