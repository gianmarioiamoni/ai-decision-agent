# app/ui/mappers/decision_state_to_view.py
#
# Maps the DecisionState to the DecisionViewModel.
# It is used to convert the DecisionState to the DecisionViewModel.
#
# Responsibility:
# - Maps the DecisionState to the DecisionViewModel
#

from app.graph.state import DecisionState
from app.ui.view_models.decision_view_model import DecisionViewModel


def map_state_to_view_model(
    state: DecisionState,
    messages,
    report_preview,
    report_file_path,
    historical_html,
    rag_evidence_html,
) -> DecisionViewModel:
    return DecisionViewModel(
        plan=state.get("plan"),
        analysis=state.get("analysis"),
        decision=state.get("decision"),
        confidence=state.get("confidence_final"),
        messages=messages,
        report_preview=report_preview,
        report_file_path=report_file_path,
        historical_html=historical_html,
        rag_evidence_html=rag_evidence_html,
    )
