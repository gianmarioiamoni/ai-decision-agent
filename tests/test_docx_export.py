# tests/test_docx_export.py
#
# Tests for DOCX export functionality.
#

import pytest
from app.report.docx_converter import html_to_docx, create_temp_docx
import os


def test_html_to_docx_simple():
    # Test basic HTML to DOCX conversion.
    
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Report</title></head>
    <body>
        <h1>Test Decision Report</h1>
        <p>This is a test report for DOCX export.</p>
    </body>
    </html>
    """
    
    try:
        docx_bytes = html_to_docx(html)
        
        # DOCX should be generated
        assert docx_bytes is not None
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 0
        
        # DOCX should start with PK signature (ZIP format)
        assert docx_bytes[:2] == b'PK'
        
        print("✅ DOCX conversion successful")
    
    except ImportError as e:
        pytest.skip(f"python-docx not installed: {e}")


def test_create_temp_docx():
    # Test creating a temporary DOCX file.
    
    # Skip if python-docx not available
    try:
        import docx
    except ImportError as e:
        pytest.skip(f"python-docx not installed: {e}")
    
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Temp DOCX Test</h1>
        <p>This is a test paragraph.</p>
    </body>
    </html>
    """
    
    temp_path = create_temp_docx(html)
    
    # File should be created
    assert temp_path is not None
    assert os.path.exists(temp_path)
    assert temp_path.endswith('.docx')
    
    # File should have content
    file_size = os.path.getsize(temp_path)
    assert file_size > 0
    
    # Clean up
    os.remove(temp_path)
    
    print(f"✅ Temp DOCX created: {file_size} bytes")


def test_html_to_docx_with_structure():
    # Test DOCX conversion with structured content.
    
    # Skip if python-docx not available
    try:
        import docx
    except ImportError as e:
        pytest.skip(f"python-docx not installed: {e}")
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial; }
            h1 { color: #2c3e50; }
        </style>
    </head>
    <body>
        <h1>Decision Report</h1>
        <h2>Question</h2>
        <p>Should we adopt this technology?</p>
        <h2>Decision</h2>
        <p>Yes, we should proceed.</p>
        <p><strong>Confidence:</strong> 0.85</p>
    </body>
    </html>
    """
    
    docx_bytes = html_to_docx(html)
    
    assert docx_bytes is not None
    assert len(docx_bytes) > 0
    assert docx_bytes[:2] == b'PK'
    
    print("✅ Structured DOCX conversion successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

