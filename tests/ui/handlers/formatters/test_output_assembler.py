# tests/ui/handlers/formatters/test_output_assembler.py
#
# Integration tests for OutputAssembler
#

import pytest
from app.ui.handlers.formatters import OutputAssembler


class TestOutputAssembler:
    """Integration test suite for OutputAssembler following SRP."""
    
    def setup_method(self):
        """Setup assembler instance for each test."""
        self.assembler = OutputAssembler()
    
    def test_assemble_complete_result(self):
        """Test assembling complete graph result."""
        result = {
            "plan": "# Plan\n- Step 1\n- Step 2",
            "analysis": "## Analysis\nThis is the analysis",
            "decision": "### Decision\nFinal decision",
            "confidence": 0.85,
            "messages": [
                {"role": "user", "content": "Question"},
                {"role": "assistant", "content": "Answer"}
            ],
            "report_html": "<html><body>Report</body></html>",
            "report_preview": "<p>Preview</p>",
            "similar_decisions": [
                {"decision_id": "dec_1", "similarity": 0.90, "content": "Similar"}
            ],
            "rag_context": "RAG context text"
        }
        context_docs = ["Document 1", "Document 2"]
        
        output = self.assembler.assemble(result, context_docs)
        
        # Verify output tuple structure
        assert len(output) == 9
        
        # Verify each output
        plan, analysis, decision, confidence, messages, report_preview, report_file, hist, rag = output
        
        assert "Step 1" in plan
        assert "Analysis" in analysis
        assert "Decision" in decision
        assert confidence == 0.85
        assert "👤" in messages  # User icon
        assert "🤖" in messages  # Assistant icon
        assert "Preview" in report_preview
        assert report_file is not None  # File should be created
        assert "dec_1" in hist
        assert "Document 1" in rag or "Document 2" in rag
    
    def test_assemble_minimal_result(self):
        """Test assembling minimal result with defaults."""
        result = {}
        context_docs = []
        
        output = self.assembler.assemble(result, context_docs)
        
        # Should return tuple with defaults
        assert len(output) == 9
        plan, analysis, decision, confidence, messages, report_preview, report_file, hist, rag = output
        
        assert "No plan" in plan
        assert "No analysis" in analysis
        assert "No decision" in decision
        assert confidence == 0.0
        assert "No messages" in messages
        assert report_file is None  # No file for empty report
        assert "No similar" in hist
    
    def test_assemble_with_none_confidence(self):
        """Test assembling when confidence is None."""
        result = {"confidence": None}
        output = self.assembler.assemble(result, [])
        
        confidence = output[3]
        assert confidence == 0.0
    
    def test_assemble_with_string_confidence(self):
        """Test assembling when confidence is string."""
        result = {"confidence": "0.75"}
        output = self.assembler.assemble(result, [])
        
        confidence = output[3]
        assert confidence == 0.75
    
    def test_assemble_creates_temp_file(self):
        """Test that report temp file is created."""
        result = {"report_html": "<html><body>Test Report</body></html>"}
        output = self.assembler.assemble(result, [])
        
        report_file_path = output[6]
        assert report_file_path is not None
        assert report_file_path.endswith(".html")
        
        # Cleanup
        import os
        if report_file_path and os.path.exists(report_file_path):
            os.remove(report_file_path)
    
    def test_assemble_no_temp_file_for_warning(self):
        """Test that no temp file created for warning message."""
        result = {}  # Will generate warning message
        output = self.assembler.assemble(result, [])
        
        report_file_path = output[6]
        assert report_file_path is None  # No file for warning


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

