# app/graph/nodes/summarize.py
# Final summarization node and session report generation
# STEP 0.3 compliant

from app.graph.state import DecisionState
from app.report.session_report import (
    generate_session_report,
    generate_preview_html,
)


def summarize_node(state: DecisionState) -> DecisionState:
    #
    # Summarize node.
    #
    # Responsibilities:
    # - Generate final HTML session report
    # - Generate preview HTML for UI
    #
    # NOTE:
    # - No message compression here (handled by graph later)
    # - No dict return
    #

    # --------------------------------------------------
    # SESSION REPORT GENERATION
    # --------------------------------------------------

    report_html = generate_session_report(state)
    preview_html = generate_preview_html(state)

    # --------------------------------------------------
    # UPDATE STATE
    # --------------------------------------------------

    # Full report (download / persistence)
    state["justification"] = report_html

    # Preview for UI (non-domain, UI-only)
    state.input_metadata["report_preview"] = preview_html


    return state


