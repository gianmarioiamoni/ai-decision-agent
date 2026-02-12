# app/ui/handlers/formatters/historical_formatter.py
#
# Formatter for historical decisions.
# Converts similar decision data to HTML cards.
#

from .base_formatter import BaseFormatter


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
        decision_text = decision.get("decision", "")
        confidence = decision.get("confidence", 0.0)
        similarity = decision.get("similarity", 0.0)
        timestamp = decision.get("timestamp")

        timestamp_str = (
            timestamp.strftime("%Y-%m-%d %H:%M")
            if timestamp else "N/A"
        )

        # similarity color
        if similarity >= 0.85:
            sim_color = "#16a34a"
        elif similarity >= 0.75:
            sim_color = "#f59e0b"
        else:
            sim_color = "#9ca3af"

        # truncation
        short_text = decision_text[:250] + "..." if len(decision_text) > 250 else decision_text

        return f"""
            <div class="decision-card">
                <h4>Decision</h4>
                <p>{short_text}</p>
                <p><strong>Confidence:</strong> {confidence:.2f}</p>
                <p><strong>Similarity:</strong> 
                    <span style="color:{sim_color}; font-weight:bold;">
                        {similarity:.2f}
                    </span>
                </p>
                <p><strong>Timestamp:</strong> {timestamp_str}</p>
            </div>
        """




