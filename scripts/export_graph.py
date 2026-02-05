# scripts/export_graph.py

from app.graph.graph import build_graph

def export_graph() -> None:
    graph = build_graph()
    mermaid = graph.get_graph().draw_mermaid()
    with open("docs/decision_graph.mmd", "w") as f:
        f.write(mermaid)

if __name__ == "__main__":
    export_graph()
