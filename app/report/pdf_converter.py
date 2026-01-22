# app/report/pdf_converter.py
#
# PDF Converter - Converts HTML reports to PDF format.
#

from typing import Optional
import tempfile


def html_to_pdf(html_content: str) -> Optional[bytes]:
    #
    # Convert HTML content to PDF bytes.
    #
    # Args:
    #     html_content: HTML string to convert
    #
    # Returns:
    #     PDF bytes, or None if conversion fails
    #
    # Raises:
    #     ImportError: If weasyprint is not installed
    #
    
    try:
        from weasyprint import HTML
        
        # Create PDF from HTML string
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
    
    except ImportError:
        raise ImportError(
            "weasyprint is required for PDF export. "
            "Install it with: pip install weasyprint"
        )
    except Exception as e:
        print(f"[PDF] ❌ Conversion failed: {e}")
        return None


def save_html_as_pdf(html_content: str, output_path: str) -> bool:
    #
    # Save HTML content as PDF file.
    #
    # Args:
    #     html_content: HTML string to convert
    #     output_path: Path where PDF should be saved
    #
    # Returns:
    #     True if successful, False otherwise
    #
    
    try:
        pdf_bytes = html_to_pdf(html_content)
        
        if pdf_bytes is None:
            return False
        
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return True
    
    except Exception as e:
        print(f"[PDF] ❌ Failed to save PDF: {e}")
        return False


def create_temp_pdf(html_content: str) -> Optional[str]:
    #
    # Create a temporary PDF file from HTML content.
    #
    # Args:
    #     html_content: HTML string to convert
    #
    # Returns:
    #     Path to temporary PDF file, or None if conversion fails
    #
    
    try:
        pdf_bytes = html_to_pdf(html_content)
        
        if pdf_bytes is None:
            return None
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode='wb',
            suffix=".pdf",
            delete=False
        )
        temp_file.write(pdf_bytes)
        temp_file.close()
        
        return temp_file.name
    
    except Exception as e:
        print(f"[PDF] ❌ Failed to create temp PDF: {e}")
        return None

