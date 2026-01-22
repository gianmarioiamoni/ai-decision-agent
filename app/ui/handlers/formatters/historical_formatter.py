# app/ui/handlers/formatters/historical_formatter.py
#
# Formatter for historical decisions.
# Converts similar decision data to HTML cards.
#

from .base_formatter import BaseFormatter


class HistoricalFormatter(BaseFormatter):
    """
    Format historical decisions into HTML cards.
    
    Responsibility: Convert list of similar decisions to styled HTML representation.
    """
    
    def format(self, similar_decisions):
        """
        Format historical decisions into HTML.
        
        Args:
            similar_decisions: List of similar decision dictionaries
                Expected keys: decision_id, similarity, content
        
        Returns:
            HTML-formatted historical decisions string
        """
        if not similar_decisions:
            return "<p style='color: gray;'>No similar historical decisions found.</p>"
        
        cards = []
        for decision in similar_decisions:
            card_html = self._create_decision_card(decision)
            cards.append(card_html)
        
        return "".join(cards)
    
    def _create_decision_card(self, decision):
        """
        Create HTML card for a single decision.
        
        Args:
            decision: Decision dictionary with id, similarity, content
        
        Returns:
            HTML string for decision card
        """
        decision_id = decision.get('decision_id', 'Unknown')
        similarity = decision.get('similarity', 0.0)
        content = decision.get('content', '')
        
        return (
            f"<div style='border:1px solid #e2e8f0; background-color:#f9fafb; "
            f"padding:8px; margin-bottom:5px; border-radius:6px;'>"
            f"<b>ID:</b> {decision_id} &nbsp; "
            f"<b>Similarity:</b> {similarity:.2f}<br>"
            f"{content}</div>"
        )

