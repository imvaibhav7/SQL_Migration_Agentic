

___________________________________________________________________________________________________

# AI Data Migration Orchestrator (Multi-Agent System)

## Project Overview

This project implements an **AI Data Migration Orchestrator** using a **multi-agent architecture powered by LLMs**.

##  Objective

The orchestrator automatically:

1. Reads source & target schemas
2. Interprets mapping metadata
3. Generates SQL migration scripts
4. Validates transformations and risks
5. Produces human-readable explanations for auditability
6. If validation from validator agent fails then again calls sql_generator agent using feedback loop.(MAX_RETRIES=3)

## 🔄 Multi-Agent Coordination Flow

```text
                 ┌──────────────────────┐
                 │   Input Metadata     │
                 │ (schemas + mappings) │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Schema Analyst Agent │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ SQL Generator Agent  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Validation Agent    │
                 └───────┬───────┬──────┘
                         │       │
             validation OK   validation issues
                         │       │
                         ▼       ▼
               ┌──────────────────────┐
               │  Explainer Agent     │
               └──────────┬───────────┘
                          ▼
                    Output Artifacts

                         ▲
                         │
                         │ (retry with feedback)
                         │
                 ┌───────┴────────────┐
                 │ SQL Generator Agent │
                 └─────────────────────┘


##  Model Used

- **Model:** `gpt-4o-mini`
- **Temperature:** `0.0` (deterministic outputs)
- Structured JSON outputs enforced via:

```python
response_format={"type":"json_object"}

## Prompting Strategy

Each agent uses:

role-specific system prompts

strict output contracts

task-scoped instructions

This prevents role leakage and improves consistency

## Outputs Generated(after execution):
outputs/
├── sample_output.sql
├── validation_report.md
└── sql_explanation.md

## Observability
Each agent logs:

inputs
outputs
Logs are stored in: /logs

## Setup Instructions:

* Create virtual environment: python -m venv venv
* Activate: venv\Scripts\activate
* Install dependencies: pip install -r requirements.txt
* Configure API key: create .env file --> OPENAI_API_KEY=your_key_here
* Run: python main.py


Design Trade-offs:

| Decision                       | Reason                        |
| ------------------------------ | ----------------------------- |
| Multi-agent over single prompt | Better modularity & debugging |
| Hybrid deterministic logic     | Prevents hallucinations       |
| Table-by-table SQL generation  | Improves reliability          |
| Pydantic contracts             | Enforces agent interfaces     |
| Centralized LLM client         | Easy model swapping           |


