# tests/test_report_templates.py
#
# Tests for HTML report template generation
#

import pytest
from app.report.session_report import (
    generate_session_report,
    generate_preview_html,
    markdown_to_html
)
from app.report.template_loader import get_template_loader


class TestTemplateLoader:
    #
    # Test template loader functionality
    #
    
    def test_loader_loads_full_template(self):
        #
        # Test that report_full.html template can be loaded
        #
        loader = get_template_loader()
        template = loader.load_template("report_full.html")
        
        assert template is not None
        # Check that template contains expected placeholders
        template_str = template.template
        assert "$timestamp" in template_str
        assert "$question" in template_str
        assert "$plan" in template_str
    
    def test_loader_loads_preview_template(self):
        #
        # Test that report_preview.html template can be loaded
        #
        loader = get_template_loader()
        template = loader.load_template("report_preview.html")
        
        assert template is not None
        template_str = template.template
        assert "$timestamp" in template_str
        assert "$question" in template_str
    
    def test_loader_caches_templates(self):
        #
        # Test that templates are cached after first load
        #
        loader = get_template_loader()
        
        # First load
        template1 = loader.load_template("report_full.html")
        
        # Second load should return cached version
        template2 = loader.load_template("report_full.html")
        
        assert template1 is template2  # Same object


class TestReportGeneration:
    #
    # Test report generation with templates
    #
    
    def test_generate_session_report(self):
        #
        # Test full session report generation
        #
        state = {
            "question": "Should we adopt microservices?",
            "plan": "## Plan\n- Analyze requirements\n- Evaluate options",
            "analysis": "### Analysis\nPros and cons...",
            "decision": "**Decision**: Yes, adopt microservices",
            "confidence": 0.85,
            "attempts": 2,
            "messages": [
                {"role": "user", "content": "Question asked"},
                {"role": "assistant", "content": "Response given"}
            ]
        }
        
        html = generate_session_report(state)
        
        # Verify HTML structure
        assert "<!DOCTYPE html>" in html
        assert "<html lang=\"en\">" in html
        assert "Should we adopt microservices?" in html
        assert "0.85" in html
        assert "confidence-badge" in html
    
    def test_generate_preview_html(self):
        #
        # Test preview HTML generation for Gradio
        #
        state = {
            "question": "Test question",
            "plan": "Test plan",
            "analysis": "Test analysis",
            "decision": "Test decision",
            "confidence": 0.90,
            "attempts": 1,
            "messages": []
        }
        
        html = generate_preview_html(state)
        
        # Verify it's a div (not full HTML document)
        assert html.strip().startswith("<div")
        assert "<!DOCTYPE html>" not in html
        assert "Test question" in html
        assert "0.90" in html
        # Verify inline styles are present
        assert "style=" in html
    
    def test_markdown_conversion_in_report(self):
        #
        # Test that markdown is properly converted
        #
        state = {
            "question": "Test",
            "plan": "## Header\n**Bold text**\n- Item 1\n- Item 2",
            "analysis": "",
            "decision": "",
            "confidence": 0.75,
            "attempts": 1,
            "messages": []
        }
        
        html = generate_session_report(state)
        
        # Verify markdown was converted
        assert "<h2>Header</h2>" in html
        assert "<strong>Bold text</strong>" in html
        assert "<li>Item 1</li>" in html
        assert "<ul>" in html
    
    def test_empty_state_handling(self):
        #
        # Test report generation with minimal/empty state
        #
        state = {
            "question": "",
            "plan": "",
            "analysis": "",
            "decision": "",
            "confidence": None,
            "attempts": 0,
            "messages": []
        }
        
        html = generate_session_report(state)
        
        # Should generate valid HTML even with empty data
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        # Should handle empty confidence gracefully
        assert "confidence-badge" in html


class TestMarkdownConversion:
    #
    # Test markdown to HTML conversion
    #
    
    def test_markdown_headers(self):
        #
        # Test header conversion
        #
        text = "## Header 2\n### Header 3\n#### Header 4"
        html = markdown_to_html(text, inline_styles=False)
        
        assert "<h2>Header 2</h2>" in html
        assert "<h3>Header 3</h3>" in html
        assert "<h4>Header 4</h4>" in html
    
    def test_markdown_bold(self):
        #
        # Test bold text conversion
        #
        text = "This is **bold text** here"
        html = markdown_to_html(text, inline_styles=False)
        
        assert "<strong>bold text</strong>" in html
    
    def test_markdown_lists(self):
        #
        # Test list conversion
        #
        text = "- Item 1\n- Item 2\n* Item 3"
        html = markdown_to_html(text, inline_styles=False)
        
        assert "<li>Item 1</li>" in html
        assert "<li>Item 2</li>" in html
        assert "<li>Item 3</li>" in html
        assert "<ul>" in html
    
    def test_markdown_inline_styles(self):
        #
        # Test that inline_styles=True adds style attributes
        #
        text = "**Bold** text"
        html = markdown_to_html(text, inline_styles=True)
        
        assert "style=" in html
        assert "color:" in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

