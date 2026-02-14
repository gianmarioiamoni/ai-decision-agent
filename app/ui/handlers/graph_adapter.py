# app/ui/handlers/graph_adapter.py
#
# LangGraph streaming adapter – Enterprise Safe Version
#

from typing import Optional
import uuid

from app.graph.graph import build_graph
from app.graph.state_factory import create_initial_state
from app.graph.state import DecisionState
from app.graph.state_validator import StateValidator

from app.ui.handlers.formatters.output_assembler import OutputAssembler
from app.ui.handlers.html.progress_bar import render_progress_bar
from app.ui.handlers.html.tokens_status_badge import render_token_status_badge
from app.ui.components.output_messages import messages_to_chatbot
from app.ui.utils.markdown_utils import md_to_plain_text
from app.ui.contracts.ui_outputs import UIOutputs

from infrastructure.cost.token_budget_manager import TokenBudgetManager


GRAPH = build_graph()


PHASES = {
    "analyzer": ("🔵 Analyzer running…", "33%", "#3b82f6"),
    "planner":  ("🟣 Planner running…",  "66%", "#8b5cf6"),
    "decision": ("🟢 Decision running…", "100%", "#22c55e"),
    "done":     ("✅ Workflow completed", "100%", "#22c55e"),
}


# ==============================================================================
# ERROR HANDLING
# ==============================================================================

def _error_output(message: str) -> UIOutputs:
    return UIOutputs(
        plan=message,
        analysis=message,
        decision=message,
        confidence_badge_html="",
        messages=[],
        phase_badge=message,
        progress_bar=render_progress_bar("0%", "#ef4444"),
        token_status_badge="",
        report_preview="",
        report_file=None,
        historical_html="",
        rag_evidence_html="",
    )


# ==============================================================================
# STREAMING ENTRYPOINT
# ==============================================================================

def run_graph_streaming(question: str, rag_files=None, session_id: str = None):

    if session_id is None:
        session_id = str(uuid.uuid4())

    try:
        initial_state: DecisionState = create_initial_state(
            user_query=question
        )

        initial_state["session_id"] = session_id

        last_state: Optional[DecisionState] = None
        phase_badge = "⏳ Waiting…"
        progress_html = render_progress_bar("5%", "#9ca3af")

        # --------------------------------------------------
        # STREAMING (UX ONLY)
        # --------------------------------------------------
        for state in GRAPH.stream(initial_state, stream_mode="values"):

            # apply centralized state normalization layer
            state = StateValidator.normalize(state)
            last_state = state

            if state.get("analysis") and not state.get("plan"):
                phase_badge, w, c = PHASES["analyzer"]
            elif state.get("plan") and not state.get("decision"):
                phase_badge, w, c = PHASES["planner"]
            elif state.get("decision"):
                phase_badge, w, c = PHASES["decision"]
            else:
                phase_badge, w, c = "⏳ Waiting…", "5%", "#9ca3af"

            progress_html = render_progress_bar(w, c)

            print("READING STATUS FOR SESSION:", session_id)

            yield UIOutputs(
                plan=md_to_plain_text(state.get("plan") or ""),
                analysis=md_to_plain_text(state.get("analysis") or ""),
                decision="",
                confidence_badge_html="",
                messages=[],
                phase_badge=phase_badge,
                progress_bar=progress_html,
                token_status_badge="",
                report_preview="",
                report_file=None,
                historical_html="",
                rag_evidence_html="",
            ).to_tuple()

        # --------------------------------------------------
        # SAFETY CHECK
        # --------------------------------------------------
        if not last_state:
            raise RuntimeError("No final state produced")

        # --------------------------------------------------
        # FINAL ASSEMBLY
        # --------------------------------------------------
        last_state = StateValidator.normalize(last_state)

        token_status = TokenBudgetManager.get_status(session_id)
        token_status_badge = render_token_status_badge(token_status)

        assembler = OutputAssembler()
        (
            plan,
            analysis,
            decision,
            confidence_badge_html,
            _messages_html,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        ) = assembler.assemble(last_state, rag_files)

        yield UIOutputs(
            plan=plan,
            analysis=analysis,
            decision=decision,
            confidence_badge_html=confidence_badge_html,
            messages=messages_to_chatbot(
                last_state.get("messages", [])
            ),
            phase_badge=PHASES["done"][0],
            progress_bar=render_progress_bar("100%", "#22c55e"),
            token_status_badge=token_status_badge,
            report_preview=report_preview,
            report_file=report_file_path,
            historical_html=historical_html,
            rag_evidence_html=rag_evidence_html,
        ).to_tuple()

    except Exception as e:
        yield _error_output(f"❌ {str(e)}").to_tuple()
