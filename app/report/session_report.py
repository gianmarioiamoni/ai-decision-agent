# app/report/session_report.py
#
# Generates an HTML report for a decision-making session based on LangGraph state.
#
# REFACTORED: HTML templates now separated into external files for better maintainability.
# - Templates: app/report/templates/report_full.html, report_preview.html
# - Logic: Python code focuses on data preparation only
#

from datetime import datetime
from typing import Any, Dict
import re
from .template_loader import get_template_loader


def markdown_to_html(text: str, inline_styles: bool = False) -> str:
    #
    # Convert basic Markdown formatting to HTML.
    # Handles: headers (###, ####), bold (**text**), newlines, lists
    #
    # Args:
    #     text: Markdown text to convert
    #     inline_styles: If True, add inline styles for Gradio compatibility
    #
    if not text:
        return ""
    
    # Convert headers with optional inline styles
    if inline_styles:
        text = re.sub(r'^####\s+(.+)$', r'<h4 style="color: #000000; font-weight: bold; margin: 10px 0;">\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^###\s+(.+)$', r'<h3 style="color: #000000; font-weight: bold; margin: 12px 0;">\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^##\s+(.+)$', r'<h2 style="color: #000000; font-weight: bold; margin: 15px 0;">\1</h2>', text, flags=re.MULTILINE)
    else:
        text = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    
    # Convert bold text **text** to <strong>text</strong> with optional inline styles
    if inline_styles:
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: #000000; font-weight: bold;">\1</strong>', text)
    else:
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    
    # Convert bullet points (- item or * item) with optional inline styles
    if inline_styles:
        text = re.sub(r'^\s*[-*]\s+(.+)$', r'<li style="color: #000000; margin-bottom: 8px; line-height: 1.5;">\1</li>', text, flags=re.MULTILINE)
    else:
        text = re.sub(r'^\s*[-*]\s+(.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    
    # Wrap consecutive <li> items in <ul> with optional inline styles
    if inline_styles:
        text = re.sub(r'(<li.*?</li>\s*)+', r'<ul style="color: #000000; padding-left: 30px; margin: 10px 0; list-style-position: outside; list-style-type: disc;">\g<0></ul>', text, flags=re.DOTALL)
    else:
        text = re.sub(r'(<li>.*?</li>\s*)+', r'<ul>\g<0></ul>', text, flags=re.DOTALL)
    
    # Convert double newlines to paragraphs with optional inline styles
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<'):  # Don't wrap if already HTML tag
            if inline_styles:
                formatted_paragraphs.append(f'<p style="color: #000000; margin: 8px 0;">{p}</p>')
            else:
                formatted_paragraphs.append(f'<p>{p}</p>')
        else:
            formatted_paragraphs.append(p)
    
    return '\n'.join(formatted_paragraphs)


def _format_messages_html(messages: list, inline_styles: bool = False) -> str:
    #
    # Format messages list as HTML list items.
    #
    # Args:
    #     messages: List of message objects (dict or LangChain Message)
    #     inline_styles: If True, add inline styles for Gradio compatibility
    #
    # Returns:
    #     HTML string with <li> elements
    #
    messages_html = ""
    
    for msg in messages:
        # Handle both dict and LangChain Message objects
        if hasattr(msg, 'type'):  # LangChain Message object
            role = msg.type if hasattr(msg, 'type') else 'unknown'
            content = msg.content if hasattr(msg, 'content') else str(msg)
        elif isinstance(msg, dict):  # Dict format
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
        else:
            role = "unknown"
            content = str(msg)
        
        if inline_styles:
            messages_html += f'<li style="color: #000000; margin-bottom: 8px; line-height: 1.5;"><strong style="color: #000000; font-weight: bold;">{role}:</strong> {content}</li>'
        else:
            messages_html += f"<li><strong>{role}:</strong> {content}</li>"
    
    return messages_html


def _format_confidence(conf_value: Any) -> str:
    #
    # Format confidence value for display.
    #
    # Args:
    #     conf_value: Confidence value (float, int, or string)
    #
    # Returns:
    #     Formatted confidence string
    #
    if conf_value and isinstance(conf_value, (int, float)):
        return f"{conf_value:.2f} (scale: 0.0-1.0)"
    return str(conf_value) if conf_value else ""


def _prepare_report_context(state: Dict[str, Any], inline_styles: bool = False) -> Dict[str, str]:
    #
    # Prepare template context from graph state.
    #
    # Args:
    #     state: The final graph state
    #     inline_styles: If True, use inline styles for markdown conversion
    #
    # Returns:
    #     Dictionary with all template variables
    #
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    return {
        "timestamp": timestamp,
        "question": state.get("question", ""),
        "plan": markdown_to_html(state.get("plan", ""), inline_styles=inline_styles),
        "analysis": markdown_to_html(state.get("analysis", ""), inline_styles=inline_styles),
        "decision": markdown_to_html(state.get("decision", ""), inline_styles=inline_styles),
        "confidence": _format_confidence(state.get("confidence", "")),
        "attempts": str(state.get("attempts", "")),
        "messages_html": _format_messages_html(state.get("messages", []), inline_styles=inline_styles)
    }


def generate_session_report(state: Dict[str, Any]) -> str:
    #
    # Generate a self-contained HTML report from the final graph state.
    # Returns complete HTML document for download.
    #
    # REFACTORED: Now uses external template (app/report/templates/report_full.html)
    #
    # Args:
    #     state: The final graph state
    #
    # Returns:
    #     The complete HTML document for download
    #
    loader = get_template_loader()
    context = _prepare_report_context(state, inline_styles=False)
    return loader.render("report_full.html", context)


def generate_preview_html(state: Dict[str, Any]) -> str:
    #
    # Generate HTML preview for Gradio (without <html><head><body> wrapper).
    # Gradio's gr.HTML component works better with div content only.
    # All styles are inline for maximum compatibility.
    #
    # REFACTORED: Now uses external template (app/report/templates/report_preview.html)
    #
    # Args:
    #     state: The final graph state
    #
    # Returns:
    #     The HTML preview for Gradio
    #
    loader = get_template_loader()
    context = _prepare_report_context(state, inline_styles=True)
    return loader.render("report_preview.html", context)
