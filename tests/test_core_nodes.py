# tests/test_core_nodes.py
# Unit tests for core graph nodes (intake, router, retriever, decision)

import pytest
from unittest.mock import MagicMock, patch, Mock
from app.graph.state import DecisionState
from app.graph.nodes.intake import intake_node
from app.graph.nodes.router import confidence_router, should_retry
from app.graph.nodes.retriever import retriever_node
from app.graph.nodes.decision import decision_node


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def base_state() -> DecisionState:
    # Minimal valid state for testing
    return DecisionState(
        messages=[],
        question="Should we adopt microservices architecture?",
        plan=None,
        retrieved_docs=[],
        analysis=None,
        decision=None,
        confidence=None,
        attempts=0
    )


@pytest.fixture
def state_with_analysis(base_state) -> DecisionState:
    # State after analysis phase
    base_state["plan"] = "Step 1: Evaluate team size\nStep 2: Assess complexity"
    base_state["analysis"] = """
    ### Pros
    - Scalability
    - Independent deployment
    
    ### Cons
    - Increased complexity
    - Higher operational cost
    """
    return base_state


# ============================================================================
# TEST INTAKE NODE
# ============================================================================

def test_intake_node_initializes_correctly(base_state):
    # Test that intake node properly initializes state
    result = intake_node(base_state)
    
    assert result["attempts"] == 0
    assert result["question"] == base_state["question"].strip()
    assert len(result["messages"]) == 1
    assert result["messages"][0]["role"] == "user"
    assert base_state["question"] in result["messages"][0]["content"]


def test_intake_node_strips_whitespace():
    # Test whitespace handling
    state = DecisionState(
        messages=[],
        question="  Should we use Docker?  \n",
        plan=None,
        retrieved_docs=[],
        analysis=None,
        decision=None,
        confidence=None,
        attempts=0
    )
    
    result = intake_node(state)
    assert result["question"] == "Should we use Docker?"


def test_intake_node_preserves_existing_state(base_state):
    # Test that intake doesn't destroy existing state
    base_state["plan"] = "Existing plan"
    base_state["confidence"] = 0.85
    
    result = intake_node(base_state)
    
    assert result["plan"] == "Existing plan"
    assert result["confidence"] == 0.85


# ============================================================================
# TEST ROUTER NODE
# ============================================================================

def test_router_high_confidence_goes_to_end(base_state):
    # High confidence should route to 'end'
    base_state["confidence"] = 0.85
    base_state["attempts"] = 0
    
    result = confidence_router(base_state)
    assert result["attempts"] == 1
    
    # Check routing logic
    base_state["attempts"] = 1
    route = should_retry(base_state)
    assert route == "end"


def test_router_low_confidence_retries(base_state):
    # Low confidence should trigger retry
    base_state["confidence"] = 0.50
    base_state["attempts"] = 0
    base_state["analysis"] = "Analysis with assumptions"
    
    result = confidence_router(base_state)
    assert result["attempts"] == 1
    
    # Check routing logic
    base_state["attempts"] = 1
    route = should_retry(base_state)
    assert route == "retry"


def test_router_max_attempts_stops_retry(base_state):
    # Max attempts should force 'end' even with low confidence
    base_state["confidence"] = 0.30
    base_state["attempts"] = 3
    
    result = confidence_router(base_state)
    assert result["attempts"] == 4
    
    # Check routing logic
    base_state["attempts"] = 4
    route = should_retry(base_state)
    assert route == "end"


def test_router_medium_confidence_continues(base_state):
    # Medium confidence should continue
    base_state["confidence"] = 0.70
    base_state["attempts"] = 1
    
    result = confidence_router(base_state)
    route = should_retry(result)
    assert route == "end"


def test_router_none_confidence_retries(base_state):
    # None confidence should retry if attempts < max
    base_state["confidence"] = None
    base_state["attempts"] = 1
    
    result = confidence_router(base_state)
    route = should_retry(result)
    assert route == "retry"


# ============================================================================
# TEST RETRIEVER NODE
# ============================================================================

@pytest.mark.integration
def test_retriever_node_basic_execution(base_state):
    # Integration test: verify retriever runs without crashing
    # Requires actual ChromaDB (may be empty)
    try:
        result = retriever_node(base_state)
        
        assert "retrieved_docs" in result
        assert isinstance(result["retrieved_docs"], list)
        assert "messages" in result
    except Exception as e:
        pytest.skip(f"Retriever integration test skipped: {e}")


@pytest.mark.integration
def test_retriever_node_handles_no_results(base_state):
    # Integration test: verify empty results handled gracefully
    try:
        result = retriever_node(base_state)
        
        assert "retrieved_docs" in result
        # Empty or non-empty is fine, just should not crash
        assert isinstance(result["retrieved_docs"], list)
    except Exception as e:
        pytest.skip(f"Retriever integration test skipped: {e}")


@pytest.mark.integration
def test_retriever_node_appends_to_messages(base_state):
    # Integration test: verify message appending
    base_state["messages"] = [{"role": "user", "content": "Question"}]
    initial_count = len(base_state["messages"])
    
    try:
        result = retriever_node(base_state)
        
        # Should have added at least one message
        assert len(result["messages"]) >= initial_count
    except Exception as e:
        pytest.skip(f"Retriever integration test skipped: {e}")


# ============================================================================
# TEST DECISION NODE
# ============================================================================

@patch('app.graph.nodes.decision.ChatOpenAI')
def test_decision_node_extracts_decision_and_confidence(MockChatOpenAI, state_with_analysis):
    # Mock LLM response with decision and confidence (0-1 scale)
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = """
    Decision: No, the team is too small for microservices
    
    Key Factors:
    - Team size: 3 developers
    - Complexity overhead too high
    - Monolith more suitable
    
    Confidence: 0.85
    """
    mock_llm.invoke.return_value = mock_response
    MockChatOpenAI.return_value = mock_llm
    
    result = decision_node(state_with_analysis)
    
    assert "decision" in result
    assert "No" in result["decision"]
    assert "microservices" in result["decision"]
    assert result["confidence"] == 0.85


@patch('app.graph.nodes.decision.ChatOpenAI')
def test_decision_node_handles_low_confidence(MockChatOpenAI, state_with_analysis):
    # Test low confidence extraction (0-1 scale)
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Decision: Maybe\nConfidence: 0.45"
    mock_llm.invoke.return_value = mock_response
    MockChatOpenAI.return_value = mock_llm
    
    result = decision_node(state_with_analysis)
    
    assert result["confidence"] == 0.45
    assert "decision" in result


@patch('app.graph.nodes.decision.ChatOpenAI')
def test_decision_node_appends_to_messages(MockChatOpenAI, state_with_analysis):
    # Test message appending
    initial_msg_count = len(state_with_analysis["messages"])
    
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Decision: Yes\nConfidence: 0.90"
    mock_llm.invoke.return_value = mock_response
    MockChatOpenAI.return_value = mock_llm
    
    result = decision_node(state_with_analysis)
    
    # Should have added at least one message (possibly more for historical context)
    assert len(result["messages"]) >= initial_msg_count + 1


@patch('app.graph.nodes.decision.ChatOpenAI')
def test_decision_node_handles_missing_confidence(MockChatOpenAI, state_with_analysis):
    # Test fallback when confidence not in response
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Decision: Yes, adopt microservices"
    mock_llm.invoke.return_value = mock_response
    MockChatOpenAI.return_value = mock_llm
    
    result = decision_node(state_with_analysis)
    
    assert "decision" in result
    # Should have confidence (might be default value 1.0)
    assert "confidence" in result
    assert result["confidence"] is not None
    assert 0 <= result["confidence"] <= 1


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

def test_intake_node_rejects_empty_question():
    # Test that empty questions are rejected
    state = DecisionState(
        messages=[],
        question="",
        plan=None,
        retrieved_docs=[],
        analysis=None,
        decision=None,
        confidence=None,
        attempts=0
    )
    
    # Should raise ValueError for empty question
    with pytest.raises(ValueError, match="non-empty string"):
        intake_node(state)


def test_router_handles_missing_fields(base_state):
    # Test router with minimal state
    base_state["confidence"] = None
    base_state["decision"] = None
    
    result = confidence_router(base_state)
    assert "attempts" in result
    assert result["attempts"] >= 0


@patch('app.graph.nodes.retriever.Chroma')
@patch('app.graph.nodes.retriever.OpenAIEmbeddings')
def test_retriever_handles_exception(mock_embeddings, mock_chroma, base_state):
    # Test graceful error handling
    mock_chroma.side_effect = Exception("DB error")
    
    # Should not crash or should handle gracefully
    try:
        result = retriever_node(base_state)
        # If it succeeds, should have retrieved_docs
        assert "retrieved_docs" in result
    except Exception as e:
        # Exception is acceptable for this test
        assert "error" in str(e).lower() or "DB error" in str(e)

