# tests/ui/handlers/formatters/test_formatters_unit.py
#
# Unit tests for formatters without external dependencies
#

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parents[4]
sys.path.insert(0, str(project_root))


def test_message_formatter_exists():
    """Test that MessageFormatter can be imported."""
    try:
        from app.ui.handlers.formatters.message_formatter import MessageFormatter
        assert MessageFormatter is not None
    except ImportError as e:
        pytest.fail(f"Could not import MessageFormatter: {e}")


def test_report_formatter_exists():
    """Test that ReportFormatter can be imported."""
    try:
        from app.ui.handlers.formatters.report_formatter import ReportFormatter
        assert ReportFormatter is not None
    except ImportError as e:
        pytest.fail(f"Could not import ReportFormatter: {e}")


def test_historical_formatter_exists():
    """Test that HistoricalFormatter can be imported."""
    try:
        from app.ui.handlers.formatters.historical_formatter import HistoricalFormatter
        assert HistoricalFormatter is not None
    except ImportError as e:
        pytest.fail(f"Could not import HistoricalFormatter: {e}")


def test_output_assembler_exists():
    """Test that OutputAssembler can be imported."""
    try:
        from app.ui.handlers.formatters.output_assembler import OutputAssembler
        assert OutputAssembler is not None
    except ImportError as e:
        pytest.fail(f"Could not import OutputAssembler: {e}")


def test_message_formatter_format_empty():
    """Test MessageFormatter with empty messages."""
    from app.ui.handlers.formatters.message_formatter import MessageFormatter
    
    formatter = MessageFormatter()
    result = formatter.format([])
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "No messages" in result or "gray" in result.lower()


def test_message_formatter_format_user_message():
    """Test MessageFormatter with a user message."""
    from app.ui.handlers.formatters.message_formatter import MessageFormatter
    
    formatter = MessageFormatter()
    messages = [{"role": "user", "content": "Hello world"}]
    result = formatter.format(messages)
    
    assert isinstance(result, str)
    assert "Hello world" in result
    assert "user" in result.lower() or "👤" in result


def test_historical_formatter_format_empty():
    """Test HistoricalFormatter with empty decisions."""
    from app.ui.handlers.formatters.historical_formatter import HistoricalFormatter
    
    formatter = HistoricalFormatter()
    result = formatter.format([])
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "No" in result or "similar" in result.lower()


def test_historical_formatter_format_decision():
    """Test HistoricalFormatter with a decision."""
    from app.ui.handlers.formatters.historical_formatter import HistoricalFormatter
    
    formatter = HistoricalFormatter()
    decisions = [{"decision_id": "test_id", "similarity": 0.85, "content": "Test decision"}]
    result = formatter.format(decisions)
    
    assert isinstance(result, str)
    assert "test_id" in result
    assert "0.85" in result or "85" in result
    assert "Test decision" in result


def test_context_loader_exists():
    """Test that ContextLoader can be imported."""
    try:
        from app.ui.handlers.loaders.context_loader import ContextLoader
        assert ContextLoader is not None
    except ImportError as e:
        pytest.fail(f"Could not import ContextLoader: {e}")


def test_context_logger_exists():
    """Test that ContextLogger can be imported."""
    try:
        from app.ui.handlers.loaders.context_logger import ContextLogger
        assert ContextLogger is not None
    except ImportError as e:
        pytest.fail(f"Could not import ContextLogger: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

