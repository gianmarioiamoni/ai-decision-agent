# app/domain/decision/decision_summary.py

def extract_decision_summary(decision_text: str) -> str:
    #
    # Extract a concise, conversational summary from a decision text.
    #
    # Rules:
    # - Max 1–2 sentences
    # - No confidence numbers
    # - No bullet points
    # - No markdown
    #

    if not decision_text:
        return ""

    lines = [
        line.strip()
        for line in decision_text.splitlines()
        if line.strip()
    ]

    # Heuristic 1: first non-empty paragraph is almost always the core decision
    first_block = lines[0]

    # Safety: trim overly long outputs
    if len(first_block) > 300:
        return first_block[:297] + "…"

    return first_block
