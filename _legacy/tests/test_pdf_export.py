# tests/test_pdf_export.py
#
# Tests for PDF export functionality.
#

import pytest
from app.report.pdf_converter import html_to_pdf, create_temp_pdf
import os


def test_html_to_pdf_simple():
    # Test basic HTML to PDF conversion.
    
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Report</title></head>
    <body>
        <h1>Test Decision Report</h1>
        <p>This is a test report for PDF export.</p>
    </body>
    </html>
    """
    
    try:
        pdf_bytes = html_to_pdf(html)
        
        # PDF should be generated
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # PDF should start with PDF magic bytes
        assert pdf_bytes[:4] == b'%PDF'
        
        print("✅ PDF conversion successful")
    
    except ImportError as e:
        pytest.skip(f"weasyprint not installed: {e}")


def test_create_temp_pdf():
    # Test creating a temporary PDF file.
    
    # Skip if weasyprint not available
    try:
        import weasyprint
    except ImportError as e:
        pytest.skip(f"weasyprint not installed: {e}")
    
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Temp PDF Test</h1>
    </body>
    </html>
    """
    
    temp_path = create_temp_pdf(html)
    
    # File should be created
    assert temp_path is not None
    assert os.path.exists(temp_path)
    assert temp_path.endswith('.pdf')
    
    # File should have content
    file_size = os.path.getsize(temp_path)
    assert file_size > 0
    
    # Clean up
    os.remove(temp_path)
    
    print(f"✅ Temp PDF created: {file_size} bytes")


def test_html_to_pdf_with_styles():
    # Test PDF conversion with CSS styles.
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            h1 { color: #2c3e50; }
            p { color: #34495e; line-height: 1.6; }
        </style>
    </head>
    <body>
        <h1>Styled Report</h1>
        <p>This report has CSS styling.</p>
    </body>
    </html>
    """
    
    try:
        pdf_bytes = html_to_pdf(html)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'
        
        print("✅ Styled PDF conversion successful")
    
    except ImportError as e:
        pytest.skip(f"weasyprint not installed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

