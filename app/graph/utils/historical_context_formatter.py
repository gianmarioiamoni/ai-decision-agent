# app/graph/utils/historical_context_formatter.py

def format_historical_context(similar_decisions: list[dict]) -> str:
    if not similar_decisions:
        return ""

    lines = []
    for d in similar_decisions:
        decision_text = d.get("decision", "")
        confidence = d.get("confidence", 0.0)
        similarity = d.get("similarity", 0.0)

        lines.append(
            f"- Similarity {similarity:.2f} | Confidence {confidence:.2f}\n"
            f"  {decision_text}\n"
        )

    return "\n".join(lines)

