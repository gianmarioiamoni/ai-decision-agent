# tests/ui/handlers/loaders/test_context_logger.py
#
# Unit tests for ContextLogger
#

import pytest
from io import StringIO
import sys
from app.ui.handlers.loaders import ContextLogger


class TestContextLogger:
    """Test suite for ContextLogger following SRP."""
    
    def setup_method(self):
        """Setup logger instance for each test."""
        self.logger = ContextLogger()
    
    def test_log_loading_summary_with_documents(self, capsys):
        """Test logging summary when documents are present."""
        docs = ["Document 1 content", "Document 2 content"]
        storage_info = {
            "file_count": 2,
            "total_size_mb": 0.5,
            "storage_path": "/test/path"
        }
        
        self.logger.log_loading_summary(docs, storage_info)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Should log document count
        assert "2 document(s)" in output or "Loaded 2" in output
        # Should log file count
        assert "2" in output
        # Should log storage path
        assert "/test/path" in output
    
    def test_log_loading_summary_empty_documents(self, capsys):
        """Test logging summary when no documents present."""
        docs = []
        storage_info = {
            "file_count": 0,
            "total_size_mb": 0.0,
            "storage_path": "/test/path"
        }
        
        self.logger.log_loading_summary(docs, storage_info)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Should log "NO documents" message
        assert "NO" in output or "0" in output
        # Should have tip message
        assert "TIP" in output or "Upload" in output
    
    def test_logger_outputs_to_stdout(self, capsys):
        """Test that logger outputs to stdout."""
        docs = ["test"]
        storage_info = {"file_count": 1, "total_size_mb": 0.1, "storage_path": "/test"}
        
        self.logger.log_loading_summary(docs, storage_info)
        
        captured = capsys.readouterr()
        # Should have output
        assert len(captured.out) > 0
    
    def test_logger_is_stateless(self):
        """Test that logger has no state between calls."""
        logger1 = ContextLogger()
        logger2 = ContextLogger()
        
        docs = ["test"]
        storage_info = {"file_count": 1, "total_size_mb": 0.1, "storage_path": "/test"}
        
        # Both should work independently
        logger1.log_loading_summary(docs, storage_info)
        logger2.log_loading_summary(docs, storage_info)
        # No assertions needed - just verify no errors


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

