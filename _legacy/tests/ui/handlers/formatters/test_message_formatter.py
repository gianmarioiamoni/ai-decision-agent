# tests/ui/handlers/formatters/test_message_formatter.py
#
# Unit tests for MessageFormatter
#

import pytest
from app.ui.handlers.formatters import MessageFormatter


class TestMessageFormatter:
    """Test suite for MessageFormatter following SRP."""
    
    def setup_method(self):
        """Setup formatter instance for each test."""
        self.formatter = MessageFormatter()
    
    def test_format_empty_messages(self):
        """Test formatting empty message list."""
        result = self.formatter.format([])
        assert "No messages generated" in result
        assert "gray" in result.lower()
    
    def test_format_single_user_message(self):
        """Test formatting single user message."""
        messages = [{"role": "user", "content": "Hello AI"}]
        result = self.formatter.format(messages)
        
        assert "👤" in result  # User icon
        assert "user" in result.lower()
        assert "Hello AI" in result
        assert "#2563eb" in result  # User color
    
    def test_format_single_assistant_message(self):
        """Test formatting single assistant message."""
        messages = [{"role": "assistant", "content": "Hello human"}]
        result = self.formatter.format(messages)
        
        assert "🤖" in result  # Assistant icon
        assert "assistant" in result.lower()
        assert "Hello human" in result
        assert "#16a34a" in result  # Assistant color
    
    def test_format_system_message(self):
        """Test formatting system message."""
        messages = [{"role": "system", "content": "System initialized"}]
        result = self.formatter.format(messages)
        
        assert "⚙️" in result  # System icon
        assert "system" in result.lower()
        assert "System initialized" in result
        assert "#f59e0b" in result  # System color
    
    def test_format_multiple_messages(self):
        """Test formatting multiple messages."""
        messages = [
            {"role": "user", "content": "Question 1"},
            {"role": "assistant", "content": "Answer 1"},
            {"role": "user", "content": "Question 2"}
        ]
        result = self.formatter.format(messages)
        
        assert result.count("👤") == 2  # Two user messages
        assert result.count("🤖") == 1  # One assistant message
        assert "Question 1" in result
        assert "Answer 1" in result
        assert "Question 2" in result
    
    def test_format_message_with_object_type(self):
        """Test formatting message object with type attribute."""
        class MockMessage:
            def __init__(self, msg_type, content):
                self.type = msg_type
                self.content = content
        
        messages = [MockMessage("user", "Test message")]
        result = self.formatter.format(messages)
        
        assert "👤" in result
        assert "Test message" in result
    
    def test_format_unknown_role(self):
        """Test formatting message with unknown role."""
        messages = [{"role": "unknown_role", "content": "Mystery message"}]
        result = self.formatter.format(messages)
        
        assert "💬" in result  # Default icon
        assert "Mystery message" in result
        # Should have default color
    
    def test_format_malformed_message(self):
        """Test formatting malformed message object."""
        messages = ["just a string"]
        result = self.formatter.format(messages)
        
        # Should handle gracefully
        assert "💬" in result
        assert "just a string" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

