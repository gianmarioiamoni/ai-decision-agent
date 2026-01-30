# app/application/decision/decision_state_mapper.py

from datetime import datetime
from uuid import uuid4

from domain.decision.decision_record import DecisionRecord
from domain.decision.decision_validation import validate_decision_record


def map_state_to_decision_record(state: dict) -> DecisionRecord:
    # Maps a finalized DecisionState to a DecisionRecord.
    # Must be called ONLY post-SUMMARIZE.
    #
    
    record = DecisionRecord(
        decision_id=str(uuid4()),
        timestamp=datetime.utcnow(),

        question=state["question"],

        decision=state["decision"],
        confidence=state["confidence"],

        rationale=_extract_rationale(state),
        key_factors=_extract_key_factors(state),

        authoritative_context_refs=_extract_authoritative_refs(state),
        historical_context_refs=_extract_historical_refs(state),

        project_id=_extract_project_id(state),
        tags=_extract_tags(state),
    )

    validate_decision_record(record)
    return record


# ------------------------------------------------------------------
# Helper functions (pure, replaceable, testable)
# ------------------------------------------------------------------

def _extract_rationale(state: dict) -> str:
    # Prefer summarized report if present
    if state.get("report_preview"):
        return state["report_preview"]

    # Fallback to analysis
    return state.get("analysis", "")


def _extract_key_factors(state: dict) -> list[str]:
    # V1: simple heuristic, can be improved later
    return [
        "rag_enabled" if state.get("rag_context") else "no_rag",
        f"attempts_{state.get('attempts', 1)}",
    ]


def _extract_authoritative_refs(state: dict) -> list[str]:
    # You can later replace this with real IDs
    return ["organizational_context"]


def _extract_historical_refs(state: dict) -> list[str]:
    # Derived from retriever node (if any)
    docs = state.get("retrieved_docs", [])
    return [doc.metadata.get("decision_id") for doc in docs if hasattr(doc, "metadata")]


def _extract_project_id(state: dict) -> str:
    return state.get("project_id", "default")


def _extract_tags(state: dict) -> list[str]:
    return ["decision", "enterprise"]
