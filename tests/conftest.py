# tests/conftest.py
# Shared pytest fixtures and configuration

import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # Set test environment variables
    os.environ["TESTING"] = "1"
    
    # Mock OpenAI API key if not present
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "test-key-for-mocked-tests"
    
    yield
    
    # Cleanup
    if os.getenv("TESTING"):
        del os.environ["TESTING"]


# ============================================================================
# SHARED STATE FIXTURES
# ============================================================================

@pytest.fixture
def minimal_state():
    # Minimal valid DecisionState
    from app.graph.state import DecisionState
    return DecisionState(
        messages=[],
        question="Test question",
        plan=None,
        retrieved_docs=[],
        analysis=None,
        decision=None,
        confidence=None,
        attempts=0
    )


@pytest.fixture
def complete_state():
    # Fully populated DecisionState
    from app.graph.state import DecisionState
    return DecisionState(
        messages=[
            {"role": "user", "content": "Should we adopt technology X?"},
            {"role": "assistant", "content": "Let me analyze that."}
        ],
        question="Should we adopt technology X?",
        plan="Step 1: Evaluate\nStep 2: Decide",
        retrieved_docs=["doc1", "doc2"],
        analysis="Pros: A, B\nCons: C, D",
        decision="Yes, with conditions",
        confidence=0.75,
        attempts=1
    )


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_llm_response():
    # Factory for creating mock LLM responses
    def _create_response(content: str):
        from unittest.mock import MagicMock
        response = MagicMock()
        response.content = content
        return response
    return _create_response


@pytest.fixture
def mock_streaming_llm():
    # Factory for creating mock streaming LLM
    def _create_stream(chunks: list):
        from unittest.mock import MagicMock
        mock = MagicMock()
        mock.stream.return_value = iter(chunks)
        return mock
    return _create_stream


# ============================================================================
# FILE SYSTEM FIXTURES
# ============================================================================

@pytest.fixture
def temp_directory(tmp_path):
    # Temporary directory that's cleaned up automatically
    return tmp_path


# ============================================================================
# PYTEST MARKERS
# ============================================================================

# Register custom markers
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "streaming: mark test for streaming functionality")
    config.addinivalue_line("markers", "rag: mark test for RAG functionality")
    config.addinivalue_line("markers", "prompt: mark test for prompt builders")
    config.addinivalue_line("markers", "report: mark test for report generation")


# ============================================================================
# TEST COLLECTION HOOKS
# ============================================================================

def pytest_collection_modifyitems(config, items):
    # Automatically mark tests based on their path
    for item in items:
        # Mark as unit by default
        if "test_core" in str(item.fspath) or "test_streaming" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Mark streaming tests
        if "streaming" in str(item.fspath):
            item.add_marker(pytest.mark.streaming)
        
        # Mark RAG tests
        if "rag" in str(item.fspath):
            item.add_marker(pytest.mark.rag)
        
        # Mark prompt tests
        if "prompt" in str(item.fspath):
            item.add_marker(pytest.mark.prompt)
        
        # Mark report tests
        if "report" in str(item.fspath) or "pdf" in str(item.fspath) or "docx" in str(item.fspath):
            item.add_marker(pytest.mark.report)

