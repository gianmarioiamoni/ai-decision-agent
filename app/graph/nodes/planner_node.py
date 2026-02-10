# app/graph/nodes/planner_node.py
#
# Planner node (streaming-capable).
#


from app.graph.state import DecisionState
from app.prompts.builders import PlannerPromptBuilder
from langchain_core.messages import AIMessage

from infrastructure.logging.node_logger import log_node
from app.llm.llm_provider import get_llm


@log_node("planner")
def planner_node(state: DecisionState) -> DecisionState:
    #
    # Planner node (streaming-capable).
    #
    # Responsibilities:
    # - Validate input
    # - Build planning prompt
    # - Stream plan generation
    # - Commit final deterministic plan
    #

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------
    if not state["user_query"]:
        raise ValueError("Planner node requires a valid user_query")

    # Context docs provided by user (optional)
    context_docs = state["input_context_docs"]

    # ------------------------------------------------------------------
    # BUILD PROMPT
    # ------------------------------------------------------------------
    bundle = PlannerPromptBuilder.build(
        question=state["user_query"],
        context_docs=context_docs,
    )

    # ------------------------------------------------------------------
    # DEBUG LOGGING
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("🗺️  PLANNER PHASE")
    print("=" * 60)
    print(f"📝 Question: {state['user_query'][:100]}...")
    print("=" * 60)

    if bundle.rag_significant:
        print("✅ Context-Grounded Mode: Planning with organizational constraints")
    else:
        print("⚪ Generic Mode: Domain-agnostic planning")

    print("=" * 60 + "\n")

    # ------------------------------------------------------------------
    # LLM INVOCATION (STREAMING)
    # ------------------------------------------------------------------
    llm = get_llm()

    buffer: list[str] = []

    for chunk in llm.stream(
        [
            bundle.system_message,
            bundle.human_message,
        ]
    ):
        token = chunk.content or ""
        buffer.append(token)

        # 🔴 Streaming-only field (UI can read this)
        state["plan_stream"] = "".join(buffer)

    # ------------------------------------------------------------------
    # FINAL COMMIT (DETERMINISTIC)
    # ------------------------------------------------------------------
    plan_text = state.get("plan_stream", "").strip()
    state["plan"] = plan_text

    state["messages"].append(
        AIMessage(content=f"Proposed Plan:\n{plan_text}")
    )

    return state

