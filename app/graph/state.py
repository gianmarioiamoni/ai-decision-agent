# app/graph/state.py

from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class DecisionState(TypedDict):
    # ==================================================
    # CONVERSATION / OBSERVABILITY
    # ==================================================
    # Full conversational transcript (user + assistant).
    # Used for UI projection and debugging only.
    # NEVER used for routing or decision logic.
    messages: Annotated[List[BaseMessage], add_messages]

    # ==================================================
    # INPUT
    # ==================================================

    user_query: str
    input_context_docs: List[str]
    input_metadata: Dict[str, Any]
    context_hash: str

    # ==================================================
    # PLANNING
    # ==================================================

    plan: Optional[str]

    # ==================================================
    # RAG
    # ==================================================

    authoritative_context: List[str]
    general_context: List[str]
    query_similarity: List[float]
    rag_context: Optional[str]

    # ==================================================
    # ANALYSIS
    # ==================================================

    analysis: Optional[str]
    risks: List[str]
    assumptions: List[str]
    confidence_base: Optional[float]

    # ==================================================
    # DECISION
    # ==================================================

    decision: Optional[str]
    justification: Optional[str]
    confidence_final: Optional[float]

    # ==================================================
    # HISTORICAL (Phase 4)
    # ==================================================

    similar_decisions: List[Dict[str, Any]]
    historical_confidence_factor: Optional[float]

    # ==================================================
    # CONFIDENCE METRICS (Phase 6)
    # ==================================================

    # Signal for policy, not direct retry
    low_confidence: bool

    # History of final confidence values across decisions
    confidence_final_history: List[float]

    # Drift of the current confidence compared to recent history
    confidence_drift: Optional[float]

    # ==================================================
    # CONTROL / ROUTING
    # ==================================================

    attempts: int
    retry_count: int
    needs_retry: bool
    decision_finalized: bool
    used_fallback: bool

    # ==================================================
    # REPORTING / UI
    # ==================================================

    report_html: Optional[str]
    report_preview: Optional[str]

    # ==================================================
    # ERROR HANDLING
    # ==================================================

    errors: List[str]

    # ==================================================
    # IDENTITY / AUDIT
    # ==================================================

    decision_id: str
    timestamp: str  # ISO 8601, UI-friendly

    # ==================================================
    # UI SEMANTICS
    # ==================================================

    history_used: bool

    # --------------------------------------------------
    # PERSISTENCE / FINALIZATION 
    # --------------------------------------------------
    history_persisted: bool

    # ==================================================
    # STREAMING
    # ==================================================

    plan_stream: str | None
    analysis_stream: str | None

    confidence_breakdown: Dict[str, float]
    # example:
    # {
    #   "base": 0.72,
    #   "historical": 0.08,
    #   "final": 0.80
    # }
