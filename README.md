---
title: AI Decision Agent
emoji: 🧠
colorFrom: purple
colorTo: indigo
sdk: gradio
sdk_version: 6.3.0
python_version: 3.11
app_file: gradio_app.py
pinned: false
license: mit
---

# AI Decision Agent

> **Enterprise-Grade AI Decision Support System**  
> Not a chatbot. A structured decision engine with governance.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-state_machine-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Deployed on HF Spaces](https://img.shields.io/badge/Deployed-HuggingFace-yellow.svg)](https://huggingface.co/spaces)

---

# 🎯 What This Project Demonstrates

<img width="1705" height="850" alt="01 - Home page" src="https://github.com/user-attachments/assets/59628c93-d510-4ce0-9e8f-b60f9a55d584" />

This project showcases the design and implementation of a **structured AI decision-making system** built for enterprise-like environments.

Instead of wrapping a single LLM prompt, it implements:

- Multi-stage orchestration
- Authoritative RAG integration
- Historical decision modeling
- Deterministic confidence scoring
- Cost governance and token enforcement
- Cloud-ready architecture

The core idea:

> **AI should support decisions with structure, traceability, and governance — not just generate answers.**

---

# 🏆 Key Differentiators

This project stands out because it is:

- Not a chat wrapper
- Not a single prompt chain
- Not a hackathon demo

It is:

- A structured AI decision engine
- Built with governance in mind
- Designed with cost control
- Deployed publicly
- Architected for enterprise environments
- Confidence-aware and history-aware

---

# 📌 Example Use Cases

- Technology adoption decisions
- Architecture trade-off analysis
- Risk-aware planning
- Policy-constrained decision support
- Organizational governance scenarios

---

# 🏗 Technology Stack

- **Python 3.11**
- **LangGraph** – State-machine orchestration
- **LangChain** – LLM abstraction
- **OpenAI models**
- **ChromaDB** – Vector storage
- **Gradio** – UI layer
- **WeasyPrint / python-docx** – Report export
- **Pytest** – Test suite

The system is fully modular and testable, with unit and graph-level tests.

---

# ☁️ Deployment: Hugging Face Spaces

Deployed using:

- `requirements-hf.txt`
- `runtime.txt`
- Gradio entrypoint (`gradio_app.py`)
- Persistent vectorstore handling
- Filesystem constraints awareness

Public deployment required:

- Budget enforcement
- Abuse control
- Error handling
- Logging per node
- Deterministic execution separation

This reflects DevOps and runtime awareness beyond local development.

---

# 🧠 Core Architecture

## 1️⃣ Multi-Stage Decision Workflow (LangGraph)

The system is built as a **deterministic state machine** using LangGraph.

High-level pipeline:

Intake
↓
RAG Retrieval (Authoritative Context)
↓
Historical Memory Retrieval
↓
Analyzer (independent reasoning)
↓
Planner (structured evaluation)
↓
Decision Node
↓
Confidence Modeling
↓
Session Report


Key architectural characteristics:

- Explicit node orchestration
- Clear ownership of state mutation
- Deterministic execution (streaming separated from logic)
- Retry logic based on confidence thresholds
- Fallback handling

This is not prompt chaining — it is **graph-driven orchestration**.

---

## 2️⃣ Separation of Concerns (Enterprise Architecture)

The system is layered and modular:

- **UI Layer (Gradio)**
- **Graph Orchestration Layer**
- **Domain Layer (Decision, Confidence, History)**
- **RAG Layer**
- **LLM Provider Abstraction**
- **Infrastructure (logging, token budget, persistence)**

Architectural principles applied:

- Each node owns specific state fields
- PromptBuilders separated from business logic
- State normalization and validation layer
- Adapter layer between UI and Graph
- Deterministic state-driven execution
- Explicit mutation control

Every node produces a semantically complete state when invoked.

This reflects production-oriented system design.

---

## 3️⃣ Authoritative RAG Integration (ChromaDB)

The system integrates a **semantic retrieval pipeline**:

- Upload of organizational documents
- Embedding and indexing via ChromaDB
- Retrieval of relevant context
- Explicit separation between:
  - **Authoritative organizational context**
  - **Historical decisions**
  - General knowledge

Organizational documents are treated as **constraints**, not suggestions.

This enables:

- Context-aware decisions
- Reduced hallucinations
- Alignment with real business constraints

Vectorstore persistence is managed within the Hugging Face environment.

---

## 4️⃣ Historical Decision Intelligence

The system maintains long-term semantic memory of past decisions.

Capabilities:

- Similarity-based retrieval
- Historical influence modeling
- Influence factor calculation
- Confidence modulation based on precedent
- Persistence via vector storage

The decision engine does not just answer — it:

- Evaluates similar past cases
- Quantifies their influence
- Adjusts confidence accordingly

This moves the system toward **AI governance**, not just generation.

---

## 5️⃣ Deterministic Confidence Modeling

The system does not trust the LLM for confidence metrics.

Instead, it computes:

- `confidence_base`
- `historical_influence_factor`
- `confidence_final`
- Confidence label mapping
- Low-confidence signaling
- Confidence drift tracking

Confidence is calculated outside the model in a deterministic layer.

This reflects production-grade ML system thinking:
> Metrics should not depend on generative output.

---

## 6️⃣ Cognitive Separation: Analyzer vs Planner

The reasoning architecture separates:

- **Analyzer** → Independent evaluation
- **Planner** → Structured evaluation plan
- **Decision Node** → Final structured output

This reduces confirmation bias and improves reasoning robustness.

The Analyzer does not simply validate the Planner.
They are independent reasoning components orchestrated via the graph.

---

## 7️⃣ Cost Governance & Token Budget Control

A dedicated **Token Budget Manager** enforces:

- Per-session limits
- Global daily limits
- Hard LLM caps
- Abuse protection

Additional features:

- Token usage transparency in UI
- Dynamic budget indicators
- Alert thresholds (>80%)
- Explicit refusal when budget exhausted

This demonstrates awareness of:

- Cloud cost control
- Production constraints
- Public deployment sustainability

Most LLM demos ignore this entirely.

---

## 8️⃣ Audit-Ready Session Reporting

Each session generates a structured HTML report including:

- Decision
- Reasoning
- Context references
- Historical influence
- Confidence breakdown

Export options:

- HTML
- PDF
- DOCX

Reports are template-driven and structured for traceability.

This supports:

- Decision documentation
- Governance workflows
- Shareable executive summaries

---

# 🧪 Engineering Quality Signals

The project includes:

- Typed state objects
- Node-level logging decorator
- Deterministic non-streaming graph execution
- Streaming isolated to UX layer
- Explicit state validation
- Retry logic based on measurable signals
- Clean UI contract definition
- Structured domain modeling

This is engineered as a system — not a notebook.

---
# Screenshots

Homepage
<img width="1705" height="850" alt="01 - Home page" src="https://github.com/user-attachments/assets/acfba513-7b87-4abf-8186-7b10b07cdae0" />


Context Files Manager
<img width="1705" height="850" alt="02 - Context Files" src="https://github.com/user-attachments/assets/33e9cd19-53fd-4f80-a8b1-0661a2843280" />


Planning & Analysis
<img width="1705" height="850" alt="03 - Planning   Analysis" src="https://github.com/user-attachments/assets/b94f61a6-9166-4223-9ea9-582e875fee0b" />


Decision
<img width="1705" height="850" alt="04 - Decision" src="https://github.com/user-attachments/assets/dbfe0f52-ffcd-4235-8a84-47c140a0e62e" />


Messages
<img width="1705" height="850" alt="05 - Messages" src="https://github.com/user-attachments/assets/11398f77-2d9a-43c8-b1f8-2ceb210cc9c4" />


Report
<img width="1705" height="850" alt="06 - Report" src="https://github.com/user-attachments/assets/56dfc6e6-4517-4c03-85cf-feb5da4a454b" />



RAG Context & Evidence
<img width="1705" height="850" alt="07 - RAG Context   Evidende" src="https://github.com/user-attachments/assets/04d08503-eda9-4ef3-a3a8-c5580f024c5d" />



Historical Decisions
<img width="1705" height="850" alt="09 - Historical decisions" src="https://github.com/user-attachments/assets/bba00816-addb-48c9-b159-703455f4a9d2" />


---

# 📄 License

MIT

---

# 📬 Author

Gianmario  
AI & Software Engineering  

---

**AI Decision Agent**  
A structured AI governance prototype for real-world decision environments.

