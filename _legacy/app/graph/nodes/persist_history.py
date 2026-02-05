# app/graph/nodes/persist_history.py

from app.graph.state import DecisionState
from domain.decision.decision_mapper import map_state_to_decision_record
from infrastructure.memory.historical_writer import HistoricalDecisionWriter


def persist_history_node(
    state: DecisionState,
    historical_writer: HistoricalDecisionWriter
) -> DecisionState:
    record = map_state_to_decision_record(state)
    historical_writer.persist(record)
    return state

