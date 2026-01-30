from domain.decision.decision_result import DecisionResult
from infrastructure.memory.historical_writer import HistoricalDecisionWriter
from domain.decision.decision_mapper import map_decision_result_to_record

def persist_history_node(
    decision_result: DecisionResult,
    historical_writer: HistoricalDecisionWriter
) -> DecisionResult:
    record = map_decision_result_to_record(decision_result)
    historical_writer.persist(record)
    return decision_result
