from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class DecisionState:
    # --- INPUT ---
    user_query: str
    input_context_docs: List[str] = field(default_factory=list)
    input_metadata: Dict[str, Any] = field(default_factory=dict)

    # --- PLANNING ---
    decision_type: Optional[str] = None
    analysis_plan: Optional[str] = None
    required_context: Optional[str] = None

    # --- RAG ---
    authoritative_context: List[str] = field(default_factory=list)
    general_context: List[str] = field(default_factory=list)
    query_similarity: List[float] = field(default_factory=list)

    # --- ANALYSIS ---
    reasoning: Optional[str] = None
    risks: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    confidence_base: Optional[float] = None

    # --- DECISION ---
    decision: Optional[str] = None
    justification: Optional[str] = None
    short_rationale: List[str] = field(default_factory=list)
    confidence_final: Optional[float] = None

    # --- HISTORICAL ---
    similar_decisions: List[Dict[str, Any]] = field(default_factory=list)
    historical_confidence_factor: Optional[float] = None
    historical_evidence: List[str] = field(default_factory=list)

    # --- CONTROL ---
    status: str = "INIT"
    errors: List[str] = field(default_factory=list)
    needs_retry: bool = False
