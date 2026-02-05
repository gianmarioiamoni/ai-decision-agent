# tests/ui/handlers/test_graph_handler_ui_boundary.py
#
# UI boundary test for graph_handler_parallel
#
# Purpose:
# - Verify explicit DecisionState → UI contract
# - Ensure UI receives stable, ordered outputs
# - Prevent DecisionState leakage into UI layer
#

from app.ui.handlers.graph_handler_parallel import _map_state_to_ui_outputs


def test_map_state_to_ui_outputs_contract():
    # Minimal DecisionState subset required for UI
    state = {
        "plan": "test plan",
        "analysis": "test analysis",
        "decision": "test decision",
        "confidence_final": 0.87,
    }

    chat_history = [("user", "question"), ("assistant", "answer")]

    outputs = _map_state_to_ui_outputs(
        state=state,  # type: ignore
        chat_history=chat_history,
        report_preview="<p>preview</p>",
        report_file_path="/tmp/report.pdf",
        historical_html="<p>history</p>",
        rag_evidence_html="<p>rag</p>",
    )

    assert outputs == (
        "test plan",
        "test analysis",
        "test decision",
        0.87,
        chat_history,
        "<p>preview</p>",
        "/tmp/report.pdf",
        "<p>history</p>",
        "<p>rag</p>",
    )
