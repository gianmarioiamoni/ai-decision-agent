from typing import NamedTuple, Optional, List


class UIOutputs(NamedTuple):
    #
    # Canonical UI output contract for Gradio layer.
    # 
    # This is the single source of truth for:
    # - Output order
    # - Output count
    # - Output types
    # 
    # Any change here MUST be reflected in Gradio outputs.
    #

    plan: str
    analysis: str
    decision: str
    confidence_badge_html: str
    messages: List
    phase_badge: str
    progress_bar: str
    report_preview: str
    report_file: Optional[str]
    historical_html: str
    rag_evidence_html: str

    def to_tuple(self):
        # Convert to tuple in strict order expected by Gradio.
        return (
            self.plan,
            self.analysis,
            self.decision,
            self.confidence_badge_html,
            self.messages,
            self.phase_badge,
            self.progress_bar,
            self.report_preview,
            self.report_file,
            self.historical_html,
            self.rag_evidence_html,
        )
