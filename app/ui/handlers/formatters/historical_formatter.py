# app/ui/handlers/formatters/historical_formatter.py
#
# Formatter for historical decisions.
# Converts similar decision data to HTML cards.
#

from .base_formatter import BaseFormatter
from domain.decision.historical_decision_evidence import HistoricalDecisionEvidence

class HistoricalFormatter(BaseFormatter):
    # Format historical decisions into HTML cards.
    #
    # Responsibility: Convert list of similar decisions to styled HTML representation.
    
    def format(self, similar_decisions):
        # Format historical decisions into HTML.
        #
        # Args:
        #     similar_decisions: List of similar decision dictionaries
        #         Expected keys: decision_id, similarity, content
        #
        # Returns:
        #     HTML-formatted historical decisions string
        #
        if not similar_decisions:
            return "<p style='color: gray;'>No similar historical decisions found.</p>"
        
        cards = []
        for decision in similar_decisions:
            card_html = self._create_decision_card(decision)
            cards.append(card_html)
        
        return "".join(cards)
    
    def _create_decision_card(self, decision: dict) -> str:
        decision_text = decision.decision
        confidence = decision.confidence
        similarity = decision.similarity_score

        return f"""
            <div class="decision-card">
                <h4>Decision</h4>
                <p><strong>Outcome:</strong> {decision_text}</p>
                <p><strong>Confidence:</strong> {confidence:.2f}</p>
                <p><strong>Similarity:</strong> {similarity:.2f}</p>
            </div>
        """



