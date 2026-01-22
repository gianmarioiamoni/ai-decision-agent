# tests/ui/handlers/rag/test_rag_modules.py
#
# Unit tests for RAG modular components
#

import pytest
from app.ui.handlers.rag import (
    StatusMessageBuilder,
    FilePathExtractor,
    UploadResult,
    OperationLogger
)


class TestStatusMessageBuilder:
    #
    # Test suite for StatusMessageBuilder following SRP.
    #
    
    def test_upload_status_success_only(self):
        #
        # Test upload status with only successful files.
        #
        result = StatusMessageBuilder.upload_status(5, 0)
        
        assert "✅" in result
        assert "5 file(s)" in result
        assert "Failed" not in result
    
    def test_upload_status_mixed(self):
        #
        # Test upload status with both success and failures.
        #
        result = StatusMessageBuilder.upload_status(3, 2)
        
        assert "✅" in result
        assert "3 file(s)" in result
        assert "⚠️" in result
        assert "2 file(s)" in result
    
    def test_upload_status_all_failed(self):
        #
        # Test upload status when all files failed.
        #
        result = StatusMessageBuilder.upload_status(0, 5)
        
        assert "❌" in result
        assert "No files were saved" in result
    
    def test_clear_status(self):
        #
        # Test clear operation status.
        #
        result = StatusMessageBuilder.clear_status(10)
        
        assert "🗑️" in result
        assert "10 file(s)" in result
        assert "Deleted" in result
    
    def test_refresh_status(self):
        #
        # Test refresh operation status.
        #
        result = StatusMessageBuilder.refresh_status()
        
        assert "🔄" in result
        assert "refreshed" in result.lower()
    
    def test_empty_upload_status(self):
        #
        # Test empty upload status returns empty string.
        #
        result = StatusMessageBuilder.empty_upload_status()
        
        assert result == ""


class TestFilePathExtractor:
    #
    # Test suite for FilePathExtractor.
    #
    
    def test_extract_path_from_string(self):
        #
        # Test extracting path from string.
        #
        path = "/tmp/test_file.txt"
        result = FilePathExtractor.extract_path(path)
        
        assert result == path
    
    def test_extract_path_from_dict(self):
        #
        # Test extracting path from dict with 'name' key.
        #
        file_obj = {"name": "/tmp/test_file.txt", "size": 1024}
        result = FilePathExtractor.extract_path(file_obj)
        
        assert result == "/tmp/test_file.txt"
    
    def test_extract_path_from_object_with_name_attr(self):
        #
        # Test extracting path from object with 'name' attribute.
        #
        class MockFile:
            def __init__(self, path):
                self.name = path
        
        file_obj = MockFile("/tmp/test_file.txt")
        result = FilePathExtractor.extract_path(file_obj)
        
        assert result == "/tmp/test_file.txt"
    
    def test_extract_path_unknown_format_raises(self):
        #
        # Test that unknown format raises ValueError.
        #
        with pytest.raises(ValueError) as exc_info:
            FilePathExtractor.extract_path(12345)
        
        assert "Unknown file object format" in str(exc_info.value)
    
    def test_extract_paths_batch(self):
        #
        # Test extracting paths from multiple file objects.
        #
        files = [
            "/tmp/file1.txt",
            {"name": "/tmp/file2.txt"},
            type('obj', (), {'name': '/tmp/file3.txt'})()
        ]
        
        result = FilePathExtractor.extract_paths(files)
        
        assert len(result) == 3
        assert "/tmp/file1.txt" in result
        assert "/tmp/file2.txt" in result
        assert "/tmp/file3.txt" in result
    
    def test_extract_paths_skips_invalid(self):
        #
        # Test that invalid files are skipped silently.
        #
        files = [
            "/tmp/file1.txt",
            12345,  # Invalid
            {"name": "/tmp/file2.txt"}
        ]
        
        result = FilePathExtractor.extract_paths(files)
        
        assert len(result) == 2
        assert "/tmp/file1.txt" in result
        assert "/tmp/file2.txt" in result


class TestUploadResult:
    #
    # Test suite for UploadResult.
    #
    
    def test_upload_result_properties(self):
        #
        # Test UploadResult computed properties.
        #
        result = UploadResult(5, ["file1.txt", "file2.txt"])
        
        assert result.saved_count == 5
        assert result.failed_count == 2
        assert result.total_count == 7
        assert len(result.failed_files) == 2
    
    def test_upload_result_no_failures(self):
        #
        # Test UploadResult with no failures.
        #
        result = UploadResult(10, [])
        
        assert result.saved_count == 10
        assert result.failed_count == 0
        assert result.total_count == 10


class TestOperationLogger:
    #
    # Test suite for OperationLogger.
    #
    # Note: These tests verify that methods don't raise exceptions.
    # Actual output testing would require capturing stdout.
    #
    
    def test_upload_started_no_error(self):
        #
        # Test that upload_started doesn't raise.
        #
        OperationLogger.upload_started(5)  # Should not raise
    
    def test_file_processing_no_error(self):
        #
        # Test that file_processing doesn't raise.
        #
        OperationLogger.file_processing("/tmp/test.txt")  # Should not raise
    
    def test_upload_complete_no_error(self):
        #
        # Test that upload_complete doesn't raise.
        #
        OperationLogger.upload_complete(5, 2)  # Should not raise
    
    def test_clear_complete_no_error(self):
        #
        # Test that clear_complete doesn't raise.
        #
        OperationLogger.clear_complete(10)  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

