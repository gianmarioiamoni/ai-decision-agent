# app/report/session_report.py
#
# Generates an HTML report for a decision-making session
# based on DecisionState.
#

from datetime import datetime, timezone
import re

from app.graph.state import DecisionState
from .template_loader import get_template_loader


# ==========================================================
# Safety helpers
# ==========================================================


def _safe_text(value) -> str:
    """
    Ensures the value is always a string.
    Prevents 'expected string or bytes-like object, got list'.
    """
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(v) for v in value)
    return str(value)


# ==========================================================
# Helpers
# ==========================================================


def _format_messages_html(messages: list, inline_styles: bool) -> str:
    if not messages:
        return ""

    items = []

    for msg in messages:
        role = getattr(msg, "type", "unknown")
        content = _safe_text(getattr(msg, "content", ""))

        if inline_styles:
            items.append(
                f"<li style='margin-bottom:6px; color:#000000;'>"
                f"<strong>{role.capitalize()}:</strong> {content}"
                f"</li>"
            )
        else:
            items.append(f"<li><strong>{role.capitalize()}:</strong> {content}</li>")

    return "\n".join(items)


def _format_confidence(confidence: float | None) -> str:
    if confidence is None:
        return ""
    return f"{confidence:.2f} (scale: 0.0–1.0)"


def _describe_influence(score: float) -> str:
    if score >= 0.75:
        return "Strong influence from previous decisions."
    if score >= 0.5:
        return "Moderate historical influence."
    if score > 0.2:
        return "Low historical influence."
    return "No significant historical influence."


# ==========================================================
# Markdown → HTML
# ==========================================================


def markdown_to_html(text: str, inline_styles: bool = False) -> str:

    text = _safe_text(text)

    if not text:
        return ""

    color = "color:#000000;" if inline_styles else ""

    # Headers
    if inline_styles:
        text = re.sub(
            r"^####\s+(.+)$",
            rf'<h4 style="{color} font-weight:bold; margin:10px 0;">\1</h4>',
            text,
            flags=re.MULTILINE,
        )
        text = re.sub(
            r"^###\s+(.+)$",
            rf'<h3 style="{color} font-weight:bold; margin:12px 0;">\1</h3>',
            text,
            flags=re.MULTILINE,
        )
    else:
        text = re.sub(r"^####\s+(.+)$", r"<h4>\1</h4>", text, flags=re.MULTILINE)
        text = re.sub(r"^###\s+(.+)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)

    # Bold
    if inline_styles:
        text = re.sub(
            r"\*\*(.+?)\*\*",
            rf'<strong style="{color}">\1</strong>',
            text,
        )
    else:
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    # Bullet points
    if inline_styles:
        text = re.sub(
            r"^\s*[-*]\s+(.+)$",
            rf'<li style="{color} margin-bottom:6px;">\1</li>',
            text,
            flags=re.MULTILINE,
        )
    else:
        text = re.sub(
            r"^\s*[-*]\s+(.+)$",
            r"<li>\1</li>",
            text,
            flags=re.MULTILINE,
        )

    # Wrap lists
    if inline_styles:
        text = re.sub(
            r"(<li.*?</li>\s*)+",
            rf'<ul style="{color} padding-left:20px;">\g<0></ul>',
            text,
            flags=re.DOTALL,
        )
    else:
        text = re.sub(
            r"(<li>.*?</li>\s*)+",
            r"<ul>\g<0></ul>",
            text,
            flags=re.DOTALL,
        )

    # Paragraphs
    paragraphs = text.split("\n\n")
    formatted = []

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        if p.startswith("<"):
            formatted.append(p)
        else:
            if inline_styles:
                formatted.append(f'<p style="{color}">{p}</p>')
            else:
                formatted.append(f"<p>{p}</p>")

    return "\n".join(formatted)


# ==========================================================
# Context builder
# ==========================================================


def _prepare_report_context(
    state: DecisionState,
    inline_styles: bool,
) -> dict:

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    historical_influence = float(state.get("historical_influence", 0.0))
    historical_factor = float(state.get("historical_factor", 1.0))
    similar_decisions = state.get("similar_decisions", []) or []

    influence_description = _describe_influence(historical_influence)

    return {
        "timestamp": timestamp,
        "question": _safe_text(state.get("user_query")),
        "plan": markdown_to_html(state.get("plan"), inline_styles),
        "analysis": markdown_to_html(state.get("analysis"), inline_styles),
        "decision": markdown_to_html(state.get("decision"), inline_styles),
        "justification": markdown_to_html(state.get("justification"), inline_styles),
        "confidence": _format_confidence(state.get("confidence_final")),
        "messages_html": _format_messages_html(
            state.get("messages", []),
            inline_styles,
        ),
        # Historical influence
        "historical_influence": f"{historical_influence:.2f}",
        "historical_factor": f"{historical_factor:.2f}",
        "historical_decisions_count": len(similar_decisions),
        "historical_influence_description": influence_description,
    }


# ==========================================================
# Public API
# ==========================================================


def generate_session_report(state: DecisionState) -> str:
    loader = get_template_loader()
    context = _prepare_report_context(state, inline_styles=False)
    return loader.render("report_full.html", context)


def generate_preview_html(state: DecisionState) -> str:
    loader = get_template_loader()
    context = _prepare_report_context(state, inline_styles=True)
    return loader.render("report_preview.html", context)
