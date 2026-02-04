# tests/test_router.py

from app.graph.router import decision_router

def test_router_returns_valid_route():
    state = {
        "confidence_base": 0.9,
        "needs_retry": False,
        "attempts": 0,
        "decision_finalized": False,
        "analysis": "ok"
    }

    route = decision_router(state)
    assert route in {"retry", "continue", "fallback", "end"}
