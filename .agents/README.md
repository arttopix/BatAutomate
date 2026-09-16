# AI Developer Agent Guidelines (.agents/)

> **Workspace Customization Root for AI Pair-Programming Assistants**  
> This `.agents/` directory defines architecture standards, development conventions, and operational rules for AI coding assistants (such as Antigravity IDE) working on the **BAT Automate** project.  
> *(Note: This directory is strictly for AI developer tooling and is completely separate from `bat-worker`, which is the unattended runtime robot daemon).*

---

## 1. Directory Structure & Workspace Rules

Antigravity IDE automatically discovers and loads all rule files located within `.agents/rules/` into the agent's context.

```text
.agents/
├── README.md                 # Overview of workspace customizations and guidelines
├── rules/                    # Modular rule definitions (auto-injected by Antigravity)
│   ├── architecture.md       # Core principles, system boundaries, and Project Bundle design
│   ├── coding_standards.md   # Python conventions, BaseAction patterns, CLI, No Emojis
│   ├── error_handling.md     # Technical vs. Business exceptions and error telemetry
│   ├── logging.md            # Structured JSON logs, variable sanitization, business metrics
│   ├── git_workflow.md       # Conventional Commits, branch naming, repository hygiene
│   ├── collaboration.md      # Developer collaboration protocols, blueprint-first, safety
│   ├── testing_standards.md  # Pytest requirements and benchmark regression testing
│   └── security.md           # Secret masking, zero credential leakage, local data privacy
└── skills/                   # (Optional) On-demand workflow runbooks and procedures
```

### Modular Rule Descriptions

| Rule Document | Scope and Primary Responsibilities |
| :--- | :--- |
| **`architecture.md`** | Open-source principles, Zero-License Office requirement (no MS Excel needed), Local AI-Native architecture (SLMs on CPU), and module boundaries. |
| **`coding_standards.md`** | Python 3.10+ typing, Pydantic schemas, `BaseAction` inheritance, safe `${var}` interpolation, standard CLI commands, and the strict **No Emojis** policy. |
| **`error_handling.md`** | Strict distinction between Technical Exceptions (RPA Dev) and Business Exceptions (business owner), with structured JSON telemetry. |
| **`logging.md`** | Automatic structured JSON log generation (`logs/log_YYYYMMDD_HHMMSS.json`), internal variable redaction (`__*`), and business impact metrics (Hours/Cost Saved). |
| **`git_workflow.md`** | Conventional Commits standard (`feat:`, `fix:`, `docs:`, etc.), branch naming strategies, and exclusions (no commits of `.venv`, `logs`, or credentials). |
| **`collaboration.md`** | Requirement to present blueprints before writing large code blocks, terminal execution permissions, and keeping documentation up to date. |
| **`testing_standards.md`** | `pytest` test suites for `bat-core` and end-to-end regression validation using real benchmark flows (e.g., `rpachallenge`). |
| **`security.md`** | Zero credential leakage (no hardcoded tokens/secrets), environment variable usage, and local on-device data privacy guarantees. |

---

## 2. BAT Automate Project Highlights

- **Local AI-Native Architecture:** Designed from the ground up for on-device Small Language Models (SLMs) running 100% on CPU (e.g., Qwen, Llama via `llama-cpp-python`, ONNX, or Ollama). Features include autonomous flow generation, self-healing selectors, and business-language error translation without cloud API costs or data leakage.
- **Zero-License Dependency for Office:** Never require Microsoft 365 or locally installed Microsoft Excel. All spreadsheet processing (`.xlsx`, `.csv`) is handled via high-performance libraries (`openpyxl`, `pandas`).
- **Business-First Mindset:** Telemetry and dashboards track real business impact (Transactions Processed, Hours Saved, Financial ROI) rather than raw technical stack traces alone.
- **Free Unlimited Unattended Workers:** Deploy worker daemons across unlimited legacy PCs, virtual machines, or edge devices without licensing constraints or worker fees.
- **Python Power and Extensibility:** Clean plugin architecture for actions (`BaseAction`), supporting Web (Playwright), API, Database, and Custom Python scripting.

---

## 3. Core Architecture and Modules

```text
BatAutomate/
├── bat-core/           # Python runtime engine, flow interpreter, action plugins, models
├── flows/              # Workflows & self-contained project bundles
│   ├── @shared/        # Reusable cross-project subflows (LINE alerts, SSO auth)
│   └── benchmarks/     # Standardized validation flows (rpachallenge)
├── logs/               # Structured execution JSON logs
├── bat-studio/         # Visual flow designer and selector inspector (Tauri + React)
├── bat-orchestrator/   # Central dashboard, scheduler, LINE alerts (FastAPI + PostgreSQL + Redis)
└── bat-worker/         # Unattended background daemon (WebSocket client)
```

| Module | Core Responsibility | Primary Tech Stack |
| :--- | :--- | :--- |
| **BAT Core (`bat-core`)** | Flow execution engine, variable context evaluation, action plugin runtime | Python 3.10+, Playwright, Pandas, OpenPyXL, Pydantic |
| **BAT Studio (`bat-studio`)** | Visual drag-and-drop workflow canvas and multi-layer UI element inspector | Tauri, React, React Flow, TypeScript |
| **BAT Orchestrator (`bat-orchestrator`)** | Job scheduler, business ROI dashboard, and alerts (LINE first, Teams, Email) | FastAPI, PostgreSQL, Redis, React Dashboard |
| **BAT Worker (`bat-worker`)** | Background daemon executing tasks dispatched from Orchestrator via WebSocket | Python Service, WebSocket Client |

---

## 4. Project Bundle Architecture & Lifecycle

Enterprise automations are organized into self-contained Project Bundles:

```text
flows/
├── @shared/                                # Shared reusable subflows (LINE Alert, SSO Login)
└── accounting/                             # Department-level grouping
    └── invoice_tax_filing/                 # Self-contained project bundle
        ├── flow.json                       # Entry point definition
        ├── subflows/                       # Internal subflow routines
        └── assets/                         # Templates, schemas, and assets
```

### Unattended Robot Deployment Lifecycle:
1. **Local Development:** Develop and verify locally using relative paths and CLI runners.
2. **Packaging:** Bundle project directory into an autonomous distribution archive (`.batpkg` / `.zip`) including required `@shared/` dependencies.
3. **Distribution & Cache:** Target workers download and cache packages securely from the Orchestrator.
4. **Sandbox Execution:** Extract package to an isolated job sandbox to prevent path conflicts.
5. **Telemetry & Streaming:** Execute via `bat-core` and stream structured JSON logs and screenshots back via WebSocket.

---

## 5. Agent-to-Agent (A2A) Hybrid Protocol

All future inter-agent communication between **Agent Orchestrator** and **Agent Worker** must strictly conform to the **Hybrid Protocol** (documented in `.agents/rules/architecture.md`):
- **Transport & State Envelope:** Real-time bi-directional network messaging using structured JSON over WebSocket (for millisecond latency, deterministic status transitions, and zero hallucination).
- **Cognitive Agent Payload:** Markdown summaries delivered inside the JSON envelope (`agent_report_md`) for natural-language agent diagnosis and human oversight.

---

## 6. Development Roadmap

- [ ] **Phase 1: Foundation and Core Engine (`bat-core`)**
  - [x] Flow JSON Schema and Pydantic validation models
  - [x] Core Interpreter, Variable Context, and `${var}` evaluation engine
  - [x] Core Actions: Web (Playwright), Excel (`openpyxl`), Logic, HTTP API
  - [x] Structured JSON logging (`logs/log_YYYYMMDD_HHMMSS.json`)
  - [x] Global CLI & Smart Flow Resolver (`batautomate list`, `batautomate run <flow>`)
  - [x] Project Bundle architecture (`flow.call`, `@shared/` integration)
- [ ] **Phase 2: Visual Designer and Selector Inspector (`bat-studio`)**
  - Visual canvas using React Flow inside a Tauri desktop shell
  - Multi-layer selector inspector (XPath, ID, Text, CSS)
  - Local debugging and step-through runner
- [ ] **Phase 3: Central Server and Business Dashboard (`bat-orchestrator`)**
  - Backend API (FastAPI) + PostgreSQL + Redis
  - Business ROI dashboard (hours and financial metrics)
  - Real-time notification dispatch (LINE Messaging API priority, Teams, Email)
- [ ] **Phase 4: Unattended Worker Daemon (`bat-worker`)**
  - Persistent WebSocket service communicating with Orchestrator
  - Process isolation, real-time log streaming, and error screenshot capture
- [ ] **Phase 5: Desktop Automation and Open-Source Release**
  - Windows UI automation (`uiautomation`)
  - Docker Compose 1-click deployment and GitHub documentation
- [ ] **Phase 6: Local AI-Native Agentic Capabilities**
  - CPU-based SLM integration (Qwen, Llama via GGUF / Ollama)
  - Self-healing selectors and autonomous decision steps
  - Copilot for natural language flow generation and error diagnosis

---

## 6. License

This project is licensed under the terms of the MIT License.
