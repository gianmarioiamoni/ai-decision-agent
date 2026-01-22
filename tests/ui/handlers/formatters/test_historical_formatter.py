# tests/ui/handlers/formatters/test_historical_formatter.py
#
# Unit tests for HistoricalFormatter
#

import pytest
from app.ui.handlers.formatters import HistoricalFormatter


class TestHistoricalFormatter:
    """Test suite for HistoricalFormatter following SRP."""
    
    def setup_method(self):
        """Setup formatter instance for each test."""
        self.formatter = HistoricalFormatter()
    
    def test_format_empty_decisions(self):
        """Test formatting empty decisions list."""
        result = self.formatter.format([])
        assert "No similar historical decisions found" in result
        assert "gray" in result.lower()
    
    def test_format_single_decision(self):
        """Test formatting single historical decision."""
        decisions = [{
            "decision_id": "dec_001",
            "similarity": 0.85,
            "content": "Decided to adopt TypeScript"
        }]
        result = self.formatter.format(decisions)
        
        assert "dec_001" in result
        assert "0.85" in result
        assert "Decided to adopt TypeScript" in result
        assert "border" in result.lower()  # Has card styling
    
    def test_format_multiple_decisions(self):
        """Test formatting multiple historical decisions."""
        decisions = [
            {
                "decision_id": "dec_001",
                "similarity": 0.90,
                "content": "Decision 1"
            },
            {
                "decision_id": "dec_002",
                "similarity": 0.75,
                "content": "Decision 2"
            }
        ]
        result = self.formatter.format(decisions)
        
        assert "dec_001" in result
        assert "dec_002" in result
        assert "0.90" in result
        assert "0.75" in result
        assert "Decision 1" in result
        assert "Decision 2" in result
        assert result.count("<div") == 2  # Two cards
    
    def test_format_decision_with_high_similarity(self):
        """Test formatting decision with high similarity score."""
        decisions = [{
            "decision_id": "dec_high",
            "similarity": 0.99,
            "content": "Very similar decision"
        }]
        result = self.formatter.format(decisions)
        
        assert "0.99" in result
        assert "dec_high" in result
    
    def test_format_decision_with_low_similarity(self):
        """Test formatting decision with low similarity score."""
        decisions = [{
            "decision_id": "dec_low",
            "similarity": 0.25,
            "content": "Somewhat similar decision"
        }]
        result = self.formatter.format(decisions)
        
        assert "0.25" in result
        assert "dec_low" in result
    
    def test_format_decision_missing_fields(self):
        """Test formatting decision with missing fields."""
        decisions = [{}]  # Empty decision dict
        result = self.formatter.format(decisions)
        
        assert "Unknown" in result  # Default ID
        assert "0.00" in result  # Default similarity
    
    def test_format_card_styling(self):
        """Test that cards have proper HTML styling."""
        decisions = [{
            "decision_id": "test",
            "similarity": 0.80,
            "content": "Test content"
        }]
        result = self.formatter.format(decisions)
        
        # Check for styling elements
        assert "border" in result
        assert "background-color" in result
        assert "padding" in result
        assert "border-radius" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

