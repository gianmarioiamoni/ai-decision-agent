# tests/domain/metrics/test_confidence_bonus.py

from domain.metrics.confidence import compute_similarity_confidence_bonus


def test_confidence_bonus_no_evidence():
    #
    # No similarities, no confidences → no bonus
    #
    bonus = compute_similarity_confidence_bonus(
        similarities=[],
        confidences=[],
    )

    assert bonus == 0.0


def test_confidence_bonus_below_similarity_threshold():
    #
    # Similarity below threshold → ignored
    #
    bonus = compute_similarity_confidence_bonus(
        similarities=[0.5, 0.6],
        confidences=[0.9, 0.8],
        similarity_threshold=0.7,
    )

    assert bonus == 0.0


def test_confidence_bonus_above_similarity_threshold():
    #
    # One valid historical match → single bonus
    #
    bonus = compute_similarity_confidence_bonus(
        similarities=[0.8],
        confidences=[0.9],
        similarity_threshold=0.7,
        confidence_bonus=0.1,
    )

    assert bonus == 0.1


def test_confidence_bonus_multiple_matches_capped():
    #
    # Multiple valid matches → capped at max_bonus
    #
    bonus = compute_similarity_confidence_bonus(
        similarities=[0.9, 0.85, 0.8],
        confidences=[0.9, 0.8, 0.7],
        similarity_threshold=0.7,
        confidence_bonus=0.1,
        max_bonus=0.2,
    )

    assert bonus == 0.2
