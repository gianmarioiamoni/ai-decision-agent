# app/graph/nodes/planner_node.py

from langchain_openai import ChatOpenAI

from app.graph.state import DecisionState
from app.prompts.builders import PlannerPromptBuilder
from langchain_core.messages import AIMessage


def planner_node(state: DecisionState) -> DecisionState:
    #
    # Planner node.
    #
    # Responsibilities:
    # - Validate input
    # - Build planning prompt using PlannerPromptBuilder
    # - Invoke LLM
    #
    # NOTE:

    if not state["user_query"]:
        raise ValueError("Planner node requires a valid user_query")

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
    print(f"📝 Question: {state["user_query"][:100]}...")
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
    state["plan"] = plan_text

    state["messages"].append(
        AIMessage(content=f"Proposed Plan:\n{plan_text}")
    )

    return state

