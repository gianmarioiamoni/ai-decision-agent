# app/ui/handlers/formatters/text_normalizer.py
#
# Normalizes markdown to text for UI display.
#
# Responsibility:
# - Normalizes markdown to text for UI display
#

import re


def normalize_markdown_to_text(md: str) -> str:
    if not md:
        return ""

    text = md

    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)

    # Inline code
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # Remove ALL bold / italic markers
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)

    # Remove ALL markdown headers
    text = re.sub(r"^\s{0,3}#+\s*", "", text, flags=re.MULTILINE)

    # Lists → bullets
    text = re.sub(r"^(\s*)[-*+]\s+", r"\1• ", text, flags=re.MULTILINE)

    # Remove markdown links
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Kill leftover markdown-ish patterns
    text = text.replace("**", "").replace("__", "")

    # Normalize spacing
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
