# app/graph/graph.py

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver

from .state import DecisionState

# Import node functions
from .nodes.intake import intake_node
from .nodes.planner import planner_node
from .nodes.rag_node import rag_node  # 🆕 Hybrid RAG support
from .nodes.retriever import retriever_node
from .nodes.analyzer import analyzer_node
from .nodes.decision import decision_node
from .nodes.router import confidence_router, should_retry
from .nodes.summarize import summarize_node

# Initialize the main graph with DecisionState
graph = StateGraph(DecisionState)

# Add all nodes
graph.add_node("intake", intake_node)
graph.add_node("planner", planner_node)
graph.add_node("rag", rag_node)  # 🆕 RAG context retrieval
graph.add_node("retriever", retriever_node)
graph.add_node("analyzer", analyzer_node)
graph.add_node("decision", decision_node)
graph.add_node("router", confidence_router)
graph.add_node("summarize", summarize_node)

# Entry point
graph.set_entry_point("intake")

# Linear flow with RAG integration
graph.add_edge("intake", "planner")
graph.add_edge("planner", "rag")        # 🆕 RAG after planning
graph.add_edge("rag", "retriever")      # 🆕 Then historical retrieval
graph.add_edge("retriever", "analyzer")
graph.add_edge("analyzer", "decision")
graph.add_edge("decision", "router")

# Conditional routing based on confidence
graph.add_conditional_edges(
    "router",
    should_retry,
    {
        "retry": "retriever",
        "end": "summarize",
    },
)

# End of graph
graph.add_edge("summarize", "__end__")

# Thread-level persistence (in-memory for now)
checkpointer = InMemorySaver()

# Compile graph
compiled_graph = graph.compile(checkpointer=checkpointer)
