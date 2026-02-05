# AI-Engineer-M3-NLP-LLM

Capstone Project — Human Capital Multi-Agent RAG System

## Overview

This project implements a **multi-agent Retrieval-Augmented Generation (RAG) architecture** for Human Capital use cases (talent search, skill intelligence, interview support, and governance).

The system is designed with **enterprise-grade separation of concerns**, where orchestration, agents, tools, infrastructure, and data ingestion are clearly decoupled. This makes the solution scalable, testable, and explainable — suitable for real-world production scenarios.

---

## High-Level Architecture

### Conceptual View

```
┌──────────────┐
│   Client /   │
│   API Call   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   app.py     │  ← System entrypoint
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Supervisor   │  ← Global controller & decision owner
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Router     │  ← Task classification & routing logic
└──────┬───────┘
       │
       ▼
┌───────────────────────────────────────────┐
│               Worker Agents                │
│                                           │
│  Retrieval | Ranking | Skill | Interview   │
│                 | Governance               │
└──────┬────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│    Tools     │  ← Stateless business logic
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Vector Store │  ← Qdrant (embeddings)
└──────────────┘
```

---

## Directory Structure

```
M3-CAPSTONE-PROJECT/
│
├── dataset/
│   └── dataset.xlsx              # Source dataset
│
├── script/
│   └── ingest_qdrant.py           # Offline ingestion pipeline
│
├── src/agent_humancapital/
│   ├── agents/
│   │   ├── supervisor.py          # Global orchestration brain
│   │   └── workers.py             # Agent execution logic
│   │
│   ├── orchestration/
│   │   ├── router.py              # Routing & intent classification
│   │   └── schemas.py             # Data contracts & schemas
│   │
│   ├── tools/
│   │   ├── retrieval_tools.py     # Vector search tools
│   │   ├── ranking_tools.py       # Candidate ranking logic
│   │   ├── skill_tools.py         # Skill extraction & inference
│   │   ├── interview_tools.py     # Interview Q&A generation
│   │   └── governance_tools.py    # Compliance & policy checks
│   │
│   ├── app.py                     # API / runtime entrypoint
│   ├── config.py                  # Environment & configuration
│   ├── llm.py                     # LLM abstraction layer
│   ├── prompts.py                 # Prompt templates
│   └── vectorstore.py             # Qdrant interface
│
├── tests/
│   ├── test_router.py             # Router unit tests
│   └── test_tools_smoke.py        # Tool smoke tests
│
└── README.md
```

---

## Component Responsibilities

### 1. Data & Ingestion Layer

**`dataset/dataset.xlsx`**
Raw structured data (e.g., resumes, skills, experience, metadata).

**`script/ingest_qdrant.py`**
Offline ingestion pipeline:

* Reads dataset
* Chunks textual fields
* Generates embeddings
* Stores vectors + metadata in Qdrant

This pipeline is intentionally **decoupled from runtime inference**.

---

### 2. Infrastructure Layer

**`llm.py`**
Abstracts the LLM provider (model selection, temperature, retries).

**`vectorstore.py`**
Encapsulates Qdrant operations:

* Similarity search
* Metadata filtering
* Result normalization

**`config.py`**
Centralized configuration for:

* API keys
* Endpoints
* Model & vector DB settings

**`prompts.py`**
All prompt templates live here, making reasoning logic:

* Versionable
* Auditable
* Easy to iterate

---

### 3. Orchestration Layer

**`app.py`**
System entrypoint:

* Accepts user request
* Passes request to Supervisor

**`supervisor.py`**
The **control plane** of the system:

* Owns end-to-end decision making
* Calls router
* Invokes worker agents
* Handles fallback, retries, and escalation

**`router.py`**
Determines *what kind of task* the user is asking for:

* Retrieval
* Ranking
* Skill analysis
* Interview preparation
* Governance / compliance

**`schemas.py`**
Defines strict contracts between:

* Router ↔ Agents
* Agents ↔ Tools

---

### 4. Agent Layer

**Worker agents** encapsulate reasoning and task execution.
They do **not** contain business logic — instead, they:

* Interpret intent
* Call the appropriate tool(s)
* Aggregate results

Current agents include:

* Retrieval Agent
* Ranking Agent
* Skill Intelligence Agent
* Interview Agent
* Governance Agent

---

### 5. Tool Layer

Tools are **stateless and reusable** business functions:

* `retrieval_tools.py` → vector similarity search
* `ranking_tools.py` → scoring & ordering logic
* `skill_tools.py` → skill inference & normalization
* `interview_tools.py` → interview question generation
* `governance_tools.py` → compliance, bias, and policy checks

Tools never know *who* is calling them — agents do.

---

## End-to-End Request Flow

```
User Request
   ↓
app.py
   ↓
Supervisor
   ↓
Router (intent classification)
   ↓
Selected Agent
   ↓
Relevant Tool(s)
   ↓
Vector Store / LLM
   ↓
Agent Response
   ↓
Supervisor Aggregation
   ↓
Final Output
```

---

## Design Principles

* **Separation of Concerns** — ingestion, inference, orchestration are isolated
* **Agent-Tool Decoupling** — agents reason, tools execute
* **Enterprise Readiness** — governance, schemas, tests included
* **Scalability** — easy to add new agents or tools
* **Explainability** — every decision path is explicit

---

## Testing Strategy

* **Router unit tests** validate intent classification
* **Tool smoke tests** ensure tool reliability

Future improvements:

* Supervisor flow tests
* Agent-level behavior tests
* Load & latency testing

---

## Future Enhancements

* Agent-per-file structure (one agent = one capability)
* Policy-based routing (risk & confidence aware)
* Memory & session state
* Observability (tracing per agent)
* Prompt versioning & audit logs

---

## Summary

This capstone demonstrates a **production-oriented multi-agent RAG architecture** with strong modularity, governance awareness, and extensibility — suitable for Human Capital and other enterprise AI use cases.
