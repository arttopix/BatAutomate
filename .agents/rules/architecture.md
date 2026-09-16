# Architecture Standards & Core Principles

This document defines the core architecture principles, system design, and module roles for the **BAT Automate** project.

---

## 1. Core Vision and Principles

1. **Open-Source and Free Forever:**
   - The Core engine, Studio, Orchestrator, and Worker components must remain open-source without per-bot licensing fees.
2. **Zero-License Dependency for Office:**
   - Spreadsheet processing (`.xlsx`, `.csv`) must strictly use file-level libraries (`openpyxl`, `pandas`).
   - Never require Microsoft 365 or a locally installed Microsoft Excel application on the user's or worker's machine.
3. **Business-First Mindset:**
   - Telemetry, logs, and dashboards must prioritize business metrics (transactions processed, hours saved, cost saved) rather than purely technical stack traces.
4. **Local AI-Native and Agentic Architecture:**
   - The foundational architecture is built to be Local AI-Native, focusing on on-device processing via Small Language Models (SLMs) running 100% on CPU (e.g., Qwen, Llama via `llama-cpp-python`, ONNX, or Ollama).
   - Hybrid execution: Deterministic Flow Execution (100% precision) combined with Agentic Autonomy (self-healing selectors, smart extraction, autonomous decision steps) with zero external token costs and complete data privacy.
5. **Sponsorship and Donation Roadmap:**
   - Sponsorship options (GitHub Sponsors, Open Collective) may be introduced in future phases. In the current phase, focus strictly on core features and stability.

---

## 2. Core Modules and System Boundaries

```text
BatAutomate/
├── bat-core/           # Python runtime engine, flow interpreter, actions, models
├── flows/              # Self-contained project bundles & shared flows (@shared/)
├── logs/               # Structured JSON logs
├── bat-studio/         # Visual flow designer and UI inspector (Tauri + React)
├── bat-orchestrator/   # Central dashboard, scheduler, LINE alerts (FastAPI + PostgreSQL + Redis)
└── bat-worker/         # Unattended background daemon (WebSocket client)
```

### Module Responsibilities

| Module | Core Role | Technology Stack |
| :--- | :--- | :--- |
| **`bat-core`** | Flow interpreter, headless execution, variable evaluation, action execution | Python 3.10+, Playwright, OpenPyXL, Pandas, Pydantic |
| **`bat-studio`** | Desktop visual flow designer, canvas, selector recorder/inspector | Tauri, React, React Flow, TypeScript |
| **`bat-orchestrator`** | Central scheduling, execution monitoring, business ROI dashboard, notifications | FastAPI, PostgreSQL, Redis, React Dashboard |
| **`bat-worker`** | Headless daemon running on target machines, WebSocket connection to Orchestrator | Python Daemon / Service, WebSocket client |

---

## 3. Project Bundle Architecture

Flows must follow the self-contained Project Bundle architecture:
- `flow.json`: The entry-point definition for the project.
- `subflows/`: Modular flow definitions called via `flow.call`.
- `assets/`: Project-specific assets (templates, schemas, test data).
- `@shared/`: Reusable cross-project subflows (e.g., notification dispatchers, SSO auth).

---

## 4. Decoupled AI and Sidecar Services

- AI Copilot and LLM diagnostic tools must operate as detached sidecar services or optional add-ons.
- `bat-core` must remain lean, fast, and able to execute flows without requiring heavyweight ML runtimes.
- Event hooks (`on_step_error`, `on_flow_complete`) provide integration touchpoints for AI observers.

---

## 5. Agent-to-Agent (A2A) Communication Architecture (Hybrid Protocol)

To enable future autonomous collaboration between the **Agent Orchestrator** and **Agent Worker**, all inter-agent communication must adhere to the **Hybrid Protocol**:

1. **Transport & State Envelope (WebSocket/JSON):**
   - Machine-to-machine coordination and state machines must use structured **JSON over WebSocket** (e.g. `status`, `job_id`, `timestamp`, `metrics`).
   - Ensures millisecond latency, deterministic state transitions (`PENDING`, `RUNNING`, `SUCCESS`, `FAILED`), and zero hallucination risk in workflow scheduling.
   - Remote workers must never rely on shared disk file mounting for inter-node state management.

2. **Cognitive Agent Payload (Markdown in JSON):**
   - Within the JSON message envelope, an `agent_report_md` payload field conveys natural language summaries, diagnoses, and incident reports formatted in Markdown.
   - Receiving agents (e.g. Orchestrator Copilot) ingest this Markdown payload to determine recovery strategies (e.g., auto-retry vs. human escalation via LINE).

