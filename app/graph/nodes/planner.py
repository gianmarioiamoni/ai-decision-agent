# app/graph/nodes/planner.py
# Planner node – STEP 0.3 compliant
# Uses PromptBuilder pattern, no orchestration logic

from langchain_openai import ChatOpenAI

from domain.decision.decision_state import DecisionState
from app.prompts.builders import PlannerPromptBuilder


def planner_node(state: DecisionState) -> DecisionState:
    #
    # Planner node.
    #
    # Responsibilities:
    # - Validate input
    # - Build planning prompt using PlannerPromptBuilder
    # - Invoke LLM
    # - Populate analysis_plan in DecisionState
    #
    # NOTE:

    if not state.user_query:
        raise ValueError("Planner node requires a valid user_query")

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    if not state.user_query:
        raise ValueError("Planner node requires a valid user_query")

    # Context docs provided by user (optional)
    context_docs = state.input_context_docs

    # ------------------------------------------------------------------
    # BUILD PROMPT
    # ------------------------------------------------------------------

    bundle = PlannerPromptBuilder.build(
        question=state.user_query,
        context_docs=context_docs,
    )

    # ------------------------------------------------------------------
    # DEBUG LOGGING
    # ------------------------------------------------------------------

    print("\n" + "=" * 60)
    print("🗺️  PLANNER PHASE")
    print("=" * 60)
    print(f"📝 Question: {state.user_query[:100]}...")
    print("=" * 60)

    if bundle.rag_significant:
        print("✅ Context-Grounded Mode: Planning with organizational constraints")
    else:
        print("⚪ Generic Mode: Domain-agnostic planning")

    print("=" * 60 + "\n")

    # ------------------------------------------------------------------
    # LLM INVOCATION
    # ------------------------------------------------------------------

    llm = ChatOpenAI(
        temperature=0.2,
        model="gpt-4o-mini",
    )

    response = llm.invoke(
        [
            bundle.system_message,
            bundle.human_message,
        ]
    )

    plan_text = response.content.strip()

    # ------------------------------------------------------------------
    # UPDATE STATE
    # ------------------------------------------------------------------

    state.analysis_plan = plan_text
    state.status = "PLANNED"

    return state

