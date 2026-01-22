# Project context for AI Decision Support Agent

# AI Research & Decision Support Agent - Project Context

## Obiettivo del progetto
Creare un agente AI capace di:
1. Ricevere una domanda complessa dall’utente
2. Pianificare i passi necessari per rispondere
3. Recuperare informazioni da documenti (RAG)
4. Analizzare alternative
5. Generare una decisione motivata con confidence score
6. Gestire memoria a breve e lungo termine

## Tecnologie principali
- Python 3.11+
- LangGraph (graph orchestration)
- LangChain (LLM + tools)
- ChromaDB (vector store)
- SQLite (thread persistence)
- Gradio (UI)
- Conda environment dedicato

## Architettura LangGraph

### State
```python
from langgraph.graph import MessageState
from typing_extensions import TypedDict

class DecisionState(MessageState):
    question: str
    plan: str | None
    retrieved_docs: list[str]
    analysis: str | None
    decision: str | None
    confidence: float | None

## Nodi principali

intake_node → normalizza la domanda, inizializza messaggi

planner_node → genera piano step-by-step

retriever_node → ricerca documenti in ChromaDB

analyzer_node → sintetizza pro/contro

decision_node → produce decisione + confidence

confidence_router → decide loop o stop

summarize_node → compressione messaggi

### Flow
intake → planner → retriever → analyzer → decision → confidence_router
                        ↑                        ↓
                        ←←←← retry ←←←←
                                  ↓
                               summarize → END
## Memory Management

Short-term → MessageState.messages

Long-term → ChromaDB + SQLite persistence

Trim messages: lasciare solo gli ultimi N

Summarization node per compressione

## Repository Structure
ai-decision-agent/
│
├── app/
│   ├── graph/
│   │   ├── state.py
│   │   ├── nodes/
│   │   │   ├── intake.py
│   │   │   ├── planner.py
│   │   │   ├── retriever.py
│   │   │   ├── analyzer.py
│   │   │   ├── decision.py
│   │   │   ├── summarize.py
│   │   │   └── router.py
│   │   └── graph.py
│   │
│   ├── memory/
│   │   ├── short_term.py
│   │   └── long_term.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── vectorstore.py
│   │   └── loaders.py
│   │
│   ├── ui/
│   │   └── gradio_app.py
│   │
│   └── main.py
│
├── data/
│   └── documents/
├── tests/
├── memory.db
├── requirements.txt
├── README.md
└── pyproject.toml

## Roadmap di sviluppo

Week 1: Core graph + CLI

Week 2: RAG + Memory (Chroma + SQLite)

Week 3: Gradio UI + Portfolio polish

## Note strategiche

Presentazione: “AI Decision Support Agent powered by LangGraph”

Evitare la parola “chatbot” per posizionamento business

Testa nodi singolarmente → ingegneria matura

