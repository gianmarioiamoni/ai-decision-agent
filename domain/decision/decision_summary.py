# app/domain/decision/decision_summary.py

import re


_DECISION_PATTERNS = [
    r"\bshould not\b",
    r"\bshould\b",
    r"\brecommend\b",
    r"\bthe decision\b",
    r"\bit is advised\b",
]


def extract_decision_summary(decision_text: str) -> str:
    #
    # Extract a concise, conversational summary from a decision text.
    #
    # Rules:
    # - 1 sentence (max 2 if strictly needed)
    # - No confidence numbers
    # - No bullet points
    # - No markdown
    # - Focus on the actual decision, not context
    #

    if not decision_text:
        return ""

    # Normalize whitespace
    text = " ".join(decision_text.split())

    # Split into sentences (simple but robust enough here)
    sentences = re.split(r"(?<=[.!?])\s+", text)

    # 1. Try to find a strong decision sentence
    for sentence in sentences:
        lowered = sentence.lower()
        if any(re.search(p, lowered) for p in _DECISION_PATTERNS):
            return _truncate(sentence)

    # 2. Fallback: first sentence
    return _truncate(sentences[0])


def _truncate(sentence: str, max_len: int = 240) -> str:
    if len(sentence) <= max_len:
        return sentence
    return sentence[: max_len - 1] + "…"

