# app/graph/state_validator.py
#
# Centralized State Normalization Layer
# Enforces structural and type consistency of DecisionState
#

from typing import Any, Dict, List
from datetime import datetime, timezone
from langchain_core.messages import BaseMessage

from app.graph.state import DecisionState


class StateValidator:
    #
    # Centralized normalization and structural enforcement.
    # Must be applied AFTER each node execution.
    #

    @classmethod
    def normalize(cls, state: DecisionState) -> DecisionState:
        state = cls._normalize_strings(state)
        state = cls._normalize_lists(state)
        state = cls._normalize_similar_decisions(state)
        state = cls._normalize_confidence(state)
        state = cls._normalize_timestamp(state)
        return state

    # ==========================================================
    # STRING FIELDS
    # ==========================================================

    @classmethod
    def _normalize_strings(cls, state: DecisionState) -> DecisionState:

        string_fields = [
            "plan",
            "analysis",
            "decision",
            "justification",
            "rag_context",
            "plan_stream",
            "analysis_stream",
            "report_html",
            "report_preview",
        ]

        for field in string_fields:
            value = state.get(field)

            if value is None:
                continue

            if isinstance(value, list):
                state[field] = "\n\n".join(str(v) for v in value)

            elif not isinstance(value, str):
                state[field] = str(value)

        return state

    # ==========================================================
    # LIST FIELDS
    # ==========================================================

    @classmethod
    def _normalize_lists(cls, state: DecisionState) -> DecisionState:

        list_fields = [
            "input_context_docs",
            "authoritative_context",
            "general_context",
            "query_similarity",
            "risks",
            "assumptions",
            "confidence_final_history",
            "errors",
        ]

        for field in list_fields:
            value = state.get(field)

            if value is None:
                state[field] = []
            elif not isinstance(value, list):
                state[field] = [value]

        # messages must always be List[BaseMessage]
        messages = state.get("messages")
        if not isinstance(messages, list):
            state["messages"] = []

        return state

    # ==========================================================
    # SIMILAR DECISIONS
    # ==========================================================

    @classmethod
    def _normalize_similar_decisions(cls, state: DecisionState) -> DecisionState:

        similar = state.get("similar_decisions")

        if not isinstance(similar, list):
            state["similar_decisions"] = []
            return state

        normalized: List[Dict[str, Any]] = []

        for item in similar:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "context_hash": str(item.get("context_hash", "")),
                    "decision": str(item.get("decision", "")),
                    "confidence": float(item.get("confidence", 0.0)),
                    "similarity": float(item.get("similarity", 0.0)),
                    "timestamp": item.get("timestamp"),
                }
            )

        state["similar_decisions"] = normalized
        return state

    # ==========================================================
    # CONFIDENCE SAFETY
    # ==========================================================

    @classmethod
    def _normalize_confidence(cls, state: DecisionState) -> DecisionState:

        if state.get("confidence_base") is not None:
            state["confidence_base"] = float(state["confidence_base"])

        if state.get("confidence_final") is not None:
            state["confidence_final"] = float(state["confidence_final"])

        if state.get("historical_influence") is not None:
            state["historical_influence"] = float(state["historical_influence"])

        return state

    # ==========================================================
    # TIMESTAMP SAFETY
    # ==========================================================

    @classmethod
    def _normalize_timestamp(cls, state: DecisionState) -> DecisionState:

        ts = state.get("timestamp")

        if ts is None:
            state["timestamp"] = datetime.now(timezone.utc).isoformat()
            return state

        if not isinstance(ts, str):
            try:
                state["timestamp"] = ts.isoformat()
            except Exception:
                state["timestamp"] = datetime.now(timezone.utc).isoformat()

        return state
