# app/ui/utils/markdown_utils.py
"""
Markdown conversion utilities for UI display.

This module provides pure functions for converting Markdown to plain text,
preserving semantic structure while removing formatting symbols.
"""

import re


def md_to_plain_text(md: str) -> str:
    """
    Convert Markdown text to plain text for Gradio Textbox display.
    
    This function removes Markdown formatting symbols while preserving
    the semantic content and hierarchy. The original Markdown is kept
    intact in the state for HTML report generation.
    
    Transformations:
    - **bold** / __bold__ → bold
    - *italic* / _italic_ → italic
    - `code` → code
    - ### Headers → Headers (no #)
    - - lists → • lists (with preserved indentation)
    - 1. lists → 1. lists (PRESERVED for hierarchy)
    - [link](url) → link
    
    Args:
        md: Markdown-formatted string
    
    Returns:
        Plain text string with preserved hierarchical structure and visual spacing
    """
    if not md:
        return ""

    text = md

    # Remove code blocks (keep content)
    text = re.sub(r"```[\s\S]*?```", lambda m: m.group(0).replace("```", ""), text)

    # Remove inline code backticks
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # Remove bold / italic markers
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # **bold**
    text = re.sub(r"__(.*?)__", r"\1", text)      # __bold__
    text = re.sub(r"\*(.*?)\*", r"\1", text)      # *italic*
    text = re.sub(r"_(.*?)_", r"\1", text)        # _italic_

    # Remove markdown headers (###, ####, etc.)
    text = re.sub(r"^\s{0,3}#+\s*", "", text, flags=re.MULTILINE)
    
    # Convert unordered lists to bullets (PRESERVING indentation for hierarchy)
    text = re.sub(r"^(\s*)[-*+]\s+", r"\1• ", text, flags=re.MULTILINE)

    # KEEP numbered lists (1., 2., 3.) to preserve hierarchy
    # Do NOT convert them to bullets - they represent main sections

    # Remove markdown links but keep text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

