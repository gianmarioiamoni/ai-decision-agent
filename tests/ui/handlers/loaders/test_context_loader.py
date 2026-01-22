# tests/ui/handlers/loaders/test_context_loader.py
#
# Unit tests for ContextLoader
#

import pytest
from app.ui.handlers.loaders import ContextLoader


class TestContextLoader:
    """Test suite for ContextLoader following SRP."""
    
    def setup_method(self):
        """Setup loader instance for each test."""
        self.loader = ContextLoader()
    
    def test_load_returns_list(self):
        """Test that load() returns a list."""
        result = self.loader.load()
        assert isinstance(result, list)
    
    def test_get_storage_info_returns_dict(self):
        """Test that get_storage_info() returns a dictionary."""
        result = self.loader.get_storage_info()
        assert isinstance(result, dict)
    
    def test_storage_info_has_expected_keys(self):
        """Test that storage info contains expected keys."""
        info = self.loader.get_storage_info()
        
        # Check for expected keys
        assert "file_count" in info
        assert "total_size_mb" in info
        assert "storage_path" in info
    
    def test_storage_info_file_count_is_int(self):
        """Test that file_count is an integer."""
        info = self.loader.get_storage_info()
        assert isinstance(info["file_count"], int)
        assert info["file_count"] >= 0
    
    def test_storage_info_size_is_numeric(self):
        """Test that total_size_mb is numeric."""
        info = self.loader.get_storage_info()
        size = info["total_size_mb"]
        assert isinstance(size, (int, float))
        assert size >= 0
    
    def test_load_consistency(self):
        """Test that consecutive loads return consistent results."""
        result1 = self.loader.load()
        result2 = self.loader.load()
        
        # Should return same number of documents
        assert len(result1) == len(result2)
    
    def test_loader_is_stateless(self):
        """Test that loader has no state between calls."""
        loader1 = ContextLoader()
        loader2 = ContextLoader()
        
        result1 = loader1.load()
        result2 = loader2.load()
        
        # Both should return same data
        assert len(result1) == len(result2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

