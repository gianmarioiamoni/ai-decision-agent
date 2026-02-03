# domain/decision/decision_state.py
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage


@dataclass
class DecisionState:
    #
    # DecisionState class.
    #
    # Single source of truth for the decision workflow state.
    # Must reflect the ACTUAL graph execution (Phase 0).
    #

    # --------------------------------------------------
    # INPUT
    # --------------------------------------------------
    user_query: str
    input_context_docs: List[str] = field(default_factory=list)
    input_metadata: Dict[str, Any] = field(default_factory=dict)

    # --------------------------------------------------
    # PLANNING (runtime)
    # --------------------------------------------------
    plan: Optional[str] = None

    # (kept for future semantic routing / Phase 1+)
    decision_type: Optional[str] = None
    analysis_plan: Optional[str] = None
    required_context: Optional[str] = None

    # --------------------------------------------------
    # RAG
    # --------------------------------------------------
    authoritative_context: List[str] = field(default_factory=list)
    general_context: List[str] = field(default_factory=list)
    query_similarity: List[float] = field(default_factory=list)

    # --------------------------------------------------
    # ANALYSIS (runtime)
    # --------------------------------------------------
    analysis: Optional[str] = None

    # (kept for richer analyzers later)
    reasoning: Optional[str] = None
    risks: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    confidence_base: Optional[float] = None

    # --------------------------------------------------
    # DECISION
    # --------------------------------------------------
    decision: Optional[str] = None
    justification: Optional[str] = None
    short_rationale: Optional[str] = None
    confidence_final: Optional[float] = None

    # --------------------------------------------------
    # HISTORICAL
    # --------------------------------------------------
    similar_decisions: List[Dict[str, Any]] = field(default_factory=list)
    historical_confidence_factor: Optional[float] = None
    historical_evidence: List[Any] = field(default_factory=list)

    # --------------------------------------------------
    # CONVERSATION / UI
    # --------------------------------------------------
    messages: List[BaseMessage] = field(default_factory=list)

    # --------------------------------------------------
    # CONTROL
    # --------------------------------------------------
    status: str = "INIT"
    errors: List[str] = field(default_factory=list)
    needs_retry: bool = False

