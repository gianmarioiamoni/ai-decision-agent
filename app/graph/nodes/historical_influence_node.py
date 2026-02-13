# app/graph/nodes/historical_influence_node.py

from app.graph.state import DecisionState
from infrastructure.logging.node_logger import log_node


class HistoricalInfluenceNode:
    # 
    # Computes how much historical decisions influenced the current one.
    # Owner of `historical_influence`.
    #

    @log_node("historical_influence")
    def __call__(self, state: DecisionState) -> DecisionState:

        similar = state.get("similar_decisions", [])

        if not similar:
            state["historical_influence"] = 0.0
            return state

        weighted_sum = 0.0

        for item in similar:
            similarity = float(item.get("similarity", 0.0))
            confidence = float(item.get("confidence", 0.0))
            weighted_sum += similarity * confidence

        influence = weighted_sum / len(similar)

        state["historical_influence"] = round(influence, 3)

        print("HISTORICAL INFLUENCE:", state["historical_influence"])

        return state
