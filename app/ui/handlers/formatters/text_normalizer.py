# app/ui/handlers/formatters/text_normalizer.py
#
# Normalizes markdown to text for UI display.
#
# Responsibility:
# - Normalizes markdown to text for UI display
#

import re


def normalize_markdown_to_text(text: str) -> str:
    if not text:
        return ""

    lines = text.splitlines()
    normalized_lines = []

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            normalized_lines.append("")
            continue

        # Remove bold (**text**) FIRST
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)

        # Headings (###, ##, #)
        if line.startswith("###"):
            normalized_lines.append(line.replace("###", "").strip().upper())
            normalized_lines.append("")
            continue

        if line.startswith("##"):
            normalized_lines.append(line.replace("##", "").strip().upper())
            continue

        if line.startswith("#"):
            normalized_lines.append(line.replace("#", "").strip().upper())
            continue

        # Bullet points
        if line.startswith("- "):
            normalized_lines.append(f"• {line[2:].strip()}")
            continue

        if line.startswith("•"):
            normalized_lines.append(line)
            continue

        # Numbered lists: "1. text"
        if re.match(r"^\d+\.\s+", line):
            normalized_lines.append(line)
            continue

        normalized_lines.append(line)

    return "\n".join(normalized_lines)

