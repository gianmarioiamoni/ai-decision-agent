# app/graph/state.py

from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class DecisionState(TypedDict):
    # ==================================================
    # CONVERSATION STATE (UI / CHAT ONLY)
    # ==================================================

    # User ↔ Assistant messages (final output only)
    # Written exclusively by FINAL node
    messages: Annotated[List[BaseMessage], add_messages]

    # ==================================================
    # INPUT
    # ==================================================

    # Current user query
    user_query: str

    # Raw documents explicitly provided by the user
    input_context_docs: List[str]

    # Optional structured metadata (source, domain, etc.)
    input_metadata: Dict[str, Any]

    # ==================================================
    # PLANNING
    # ==================================================

    # High-level execution plan
    plan: Optional[str]

    # ==================================================
    # RAG
    # ==================================================

    # Authoritative context selected by retriever
    authoritative_context: List[str]

    # Supporting / general context
    general_context: List[str]

    # Similarity scores (parallel to retrieved chunks)
    query_similarity: List[float]

    # Final formatted RAG context injected into prompts
    rag_context: Optional[str]

    # ==================================================
    # ANALYSIS
    # ==================================================

    # Main analytical reasoning
    analysis: Optional[str]

    # Explicit risks identified
    risks: List[str]

    # Explicit assumptions
    assumptions: List[str]

    # Base confidence computed by analyzer
    confidence_base: Optional[float]

    # ==================================================
    # DECISION
    # ==================================================

    # Final decision text
    decision: Optional[str]

    # Short justification (UI-friendly)
    justification: Optional[str]

    # Final confidence after all adjustments
    confidence_final: Optional[float]

    # ==================================================
    # HISTORICAL (Phase 4 – already modeled)
    # ==================================================

    # Retrieved similar past decisions
    similar_decisions: List[Dict[str, Any]]

    # Confidence modifier derived from history
    historical_confidence_factor: Optional[float]

    # ==================================================
    # CONTROL / ROUTING
    # ==================================================

    # Number of attempts (for retry / fallback logic)
    attempts: int

    # Whether the flow requires retry
    needs_retry: bool

    # Terminal flag (router may stop execution)
    decision_finalized: bool

    # ==================================================
    # REPORTING / UI
    # ==================================================

    report_html: Optional[str]
    report_preview: Optional[str]

    # ==================================================
    # ERROR HANDLING
    # ==================================================

    errors: List[str]

