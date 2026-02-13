# app/ui/utils/markdown_utils.py
#
# Markdown conversion utilities for UI display.
# Pure function.
# Always returns a string.
# Safe against list / None inputs.
#

import re


def _normalize_to_string(value) -> str:
    # Ensures input is always a string.
    # Prevents: "expected string or bytes-like object, got 'list'"
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(v) for v in value)
    return str(value)


def md_to_plain_text(md) -> str:
    # Convert Markdown text to plain text for Gradio Textbox display.
    #
    # Transformations:
    # - **bold** → bold
    # - *italic* → italic
    # - `code` → code
    # - ### Headers → Headers
    # - - lists → • lists
    # - [link](url) → link
    #
    # Always safe for non-string inputs.

    text = _normalize_to_string(md)

    if not text:
        return ""

    # Remove code blocks (keep content)
    text = re.sub(
        r"```[\s\S]*?```",
        lambda m: m.group(0).replace("```", ""),
        text,
    )

    # Remove inline code backticks
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # Remove bold / italic markers
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)

    # Remove markdown headers
    text = re.sub(
        r"^\s{0,3}#+\s*",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Convert unordered lists to bullets
    text = re.sub(
        r"^(\s*)[-*+]\s+",
        r"\1• ",
        text,
        flags=re.MULTILINE,
    )

    # Remove markdown links but keep text
    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text,
    )

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
