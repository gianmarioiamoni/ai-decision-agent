# app/ui/view_models/decision_view_model.py
#
# DecisionViewModel is a Pydantic model that defines the data structure for the decision-related UI components.
# It is the UI contract between the UI and the backend.
# It is used to validate the data passed to the UI components and to ensure that the data is consistent.
#
# Responsibility:
# - View model for decision-related UI components
# - Provides structured data for UI rendering
# - Facilitates data flow between UI and backend, including error handling and validation
#
from typing import List, Optional
from pydantic import BaseModel


class DecisionViewModel(BaseModel):
    plan: Optional[str]
    analysis: Optional[str]
    decision: Optional[str]
    confidence: Optional[float]
    messages: list
    report_preview: Optional[str]
    report_file_path: Optional[str]
    historical_html: Optional[str]
    rag_evidence_html: Optional[str]
