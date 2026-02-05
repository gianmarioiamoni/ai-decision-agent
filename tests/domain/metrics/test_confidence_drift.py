# tests/domain/metrics/test_confidence_drift.py

from domain.metrics.confidence_drift import compute_confidence_drift


def test_confidence_drift_no_history():
    #
    # No historical confidence → no drift
    #
    drift = compute_confidence_drift(
        history=[],
        current=0.75,
    )

    assert drift == 0.0


def test_confidence_drift_positive():
    #
    # Current confidence higher than historical average → positive drift
    #
    drift = compute_confidence_drift(
        history=[0.6, 0.65, 0.7],
        current=0.8,
    )

    assert drift > 0
    assert round(drift, 3) == round(0.8 - (0.6 + 0.65 + 0.7) / 3, 3)


def test_confidence_drift_negative():
    #
    # Current confidence lower than historical average → negative drift
    #
    drift = compute_confidence_drift(
        history=[0.8, 0.85, 0.9],
        current=0.7,
    )

    assert drift < 0
    assert round(drift, 3) == round(0.7 - (0.8 + 0.85 + 0.9) / 3, 3)
