# app/ui/handlers/formatters/text_normalizer.py
#
# Normalizes text for UI display.
#
# Responsibility:
# - Normalizes text for UI display
#

import re


def normalize_markdown_to_text(text: str) -> str:
    if not text:
        return ""
   
    # log for debugging
    print(f"### Starting normalization of markdown to text")
    
    lines = text.splitlines()
    normalized_lines = []

    for line in lines:
        line = line.strip()

        # Headings (###, ##, #)
        if line.startswith("###"):
            normalized_lines.append(line.replace("###", "").strip().upper())
            normalized_lines.append("")  # spacing
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

        # Bold (**text**)
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)

        # log for debugging
        print(f"### Normalized line: {line}")

        normalized_lines.append(line)

    # log for debugging
    return_text = "\n".join(normalized_lines)
    print(f"### Final normalized text: {return_text}")

    return return_text
