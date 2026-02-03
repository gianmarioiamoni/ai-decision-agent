# app/report/session_report.py
#
# Generates an HTML report for a decision-making session
# based on DecisionState.
#
# STEP 0.4.2:
# - Report is now a pure view of DecisionState
# - No dict-based state
# - No orchestration or UI-only fields
#

from datetime import datetime, timezone
import re

from domain.decision.decision_state import DecisionState
from .template_loader import get_template_loader

def _format_messages_html(messages: list, inline_styles: bool) -> str:
    if not messages:
        return ""

    items = []

    for msg in messages:
        # LangChain BaseMessage
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", "")

        if inline_styles:
            items.append(
                f"<li style='margin-bottom: 6px;'>"
                f"<strong>{role.capitalize()}:</strong> {content}"
                f"</li>"
            )
        else:
            items.append(
                f"<li><strong>{role.capitalize()}:</strong> {content}</li>"
            )

    return "\n".join(items)




def _format_confidence(confidence: float | None) -> str:
    if confidence is None:
        return ""
    return f"{confidence:.2f} (scale: 0.0–1.0)"


def _prepare_report_context(
    state: DecisionState,
    inline_styles: bool,
) -> dict:
    # Prepare template context from DecisionState only.

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return {
        "timestamp": timestamp,
        "question": state.user_query,
        "plan": markdown_to_html(
            state.analysis_plan or "",
            inline_styles=inline_styles,
        ),
        "analysis": markdown_to_html(
            state.reasoning or "",
            inline_styles=inline_styles,
        ),
        "decision": markdown_to_html(
            state.decision or "",
            inline_styles=inline_styles,
        ),
        "confidence": _format_confidence(state.confidence_final),
        "short_rationale": markdown_to_html(
            "\n".join(f"- {r}" for r in state.short_rationale),
            inline_styles=inline_styles,
        ),
        "messages_html": _format_messages_html(state.messages, inline_styles=inline_styles),

    }

def markdown_to_html(text: str, inline_styles: bool = False) -> str:
    # Convert basic Markdown formatting to HTML.
    # Handles headers, bold text, bullet lists and paragraphs.

    if not text:
        return ""

    # Headers
    if inline_styles:
        text = re.sub(
            r"^###\s+(.+)$",
            r'<h3 style="font-weight: bold; margin: 12px 0;">\1</h3>',
            text,
            flags=re.MULTILINE,
        )
    else:
        text = re.sub(r"^###\s+(.+)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)

    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    # Bullet points
    text = re.sub(
        r"^\s*[-*]\s+(.+)$",
        r"<li>\1</li>",
        text,
        flags=re.MULTILINE,
    )

    # Wrap list items
    text = re.sub(r"(<li>.*?</li>\s*)+", r"<ul>\g<0></ul>", text, flags=re.DOTALL)

    # Paragraphs
    paragraphs = text.split("\n\n")
    formatted = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith("<"):
            formatted.append(f"<p>{p}</p>")
        else:
            formatted.append(p)

    return "\n".join(formatted)

def generate_session_report(state: DecisionState) -> str:
    # Generate full HTML report for download.

    loader = get_template_loader()
    context = _prepare_report_context(state, inline_styles=False)
    return loader.render("report_full.html", context)


def generate_preview_html(state: DecisionState) -> str:
    # Generate HTML preview for Gradio (inline styles).

    loader = get_template_loader()
    context = _prepare_report_context(state, inline_styles=True)
    return loader.render("report_preview.html", context)

