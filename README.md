# BAT Automate

> **Open-Source, Python-Powered Enterprise RPA Platform**  
> Eliminate soaring commercial RPA licensing costs with an end-to-end automation suite, business-first ROI dashboard, and 100% free unattended robots.

---

## Key Highlights

- **Zero-License Dependency:** No Microsoft 365 or Microsoft Excel installation required for spreadsheet operations (processed natively via `openpyxl` and `pandas`).
- **Business-First Dashboard:** Tailored for executives and business leaders with transparent metrics on Return on Investment (ROI), total hours saved, and tangible cost reductions.
- **Free Unlimited Unattended Workers:** Deploy robot worker daemons across any existing VMs or workstations with zero per-bot monthly licensing fees.
- **Python Power & Extensibility:** Easily extend capabilities with standard Python, integrating seamlessly with modern Web automation (Playwright), REST APIs, SQL databases, and AI models.
- **Local AI Ready (Future-Proof):** Architected to support lightweight, CPU-runnable Small Language Models (SLMs) for Studio Copilot and automated business-friendly error explanations.

---

## System Architecture (Core Modules)

BAT Automate is organized into four decoupled, modular components:

```text
BatAutomate/
├── bat-core/               # Execution Runtime & Standard Action Libraries
│   ├── actions/            # Web (Playwright), Excel, API, Logic, System
│   ├── engine/             # Flow Interpreter, Variable Context, Evaluator
│   └── models/             # Flow JSON Schema (Pydantic models)
│
├── bat-studio/             # Visual Flow Designer & UI Inspector (Desktop App)
│   ├── src/                # Tauri + React + React Flow
│   └── inspector/          # Web & Windows UI Selector Tools
│
├── bat-orchestrator/       # Central Control Hub & Business Dashboard
│   ├── api/                # FastAPI Backend, WebSocket Manager, Scheduler
│   └── web/                # React Dashboard (Business KPIs, Jobs, Logs, Assets)
│
└── bat-worker/             # Unattended / Attended Robot Daemon
    └── src/                # Windows/Linux Service, WebSocket Client, Runner
```

| Module | Role & Responsibility | Core Technology Stack |
| :--- | :--- | :--- |
| **BAT Core (`bat-core`)** | Execution engine, Flow JSON interpreter, variable state manager, Web & Excel automation | Python, Playwright, Pandas, OpenPyXL |
| **BAT Studio (`bat-studio`)** | Cross-platform desktop app for visual drag-and-drop workflow authoring & UI inspector | Tauri, React, React Flow, TypeScript |
| **BAT Orchestrator (`bat-orchestrator`)** | Centralized management hub, cron/trigger scheduler, executive ROI dashboard, and alerting | FastAPI, PostgreSQL, Redis, React, TailwindCSS |
| **BAT Worker (`bat-worker`)** | Background daemon deployed on execution targets receiving jobs via WebSocket | Python Service, WebSocket |

---

## Development Roadmap

- [ ] **Phase 1: Foundation & Core Engine (`bat-core`)**
  - [x] Flow JSON Schema and Pydantic v2 data models
  - [x] Flow Interpreter, execution context manager, and dynamic variable evaluator (`${var}`)
  - [x] Standard Action libraries: Web (Playwright sync), Excel (`openpyxl`), Logic, HTTP API
  - [x] Hierarchical Structured Logging (`logs/<flow>/<date>/<time>.json`)
  - [x] Global CLI & Smart Flow Resolver (`batautomate list`, `batautomate run <flow_name>`)
- [ ] **Phase 2: Visual Designer & Selector (`bat-studio`)**
  - Interactive drag-and-drop workflow canvas with React Flow inside Tauri shell
  - Web and desktop UI element inspectors for auto-generating reliable selectors
  - Local flow runner and step-by-step interactive debugger
- [ ] **Phase 3: Central Server & Business Dashboard (`bat-orchestrator`)**
  - High-performance REST API (FastAPI) + PostgreSQL + Redis queue
  - Executive Business Dashboard: ROI calculations, hours saved tracking, transaction audit trail
  - Multi-channel alerts on failures and daily digests (LINE Messaging API, Microsoft Teams, Email)
- [ ] **Phase 4: Unattended Agent Daemon (`bat-worker`)**
  - WebSocket agent daemon connecting worker nodes to Orchestrator
  - Isolated process runner, real-time log streaming, and failure screenshot capture
- [ ] **Phase 5: Desktop Automation & Community Open Source Release**
  - Native Windows desktop automation integration (`uiautomation`)
  - 1-Click Docker Compose deployment and GitHub community quickstart documentation
- [ ] **Phase 6: Local AI & Copilot Integration (Future Phase)**
  - Local CPU-based SLM support (such as Qwen 2.5) for Studio Copilot and plain-language root-cause analysis

---

## Quick Start (CLI)

Install `batautomate` in editable mode:

```powershell
cd bat-core
pip install -e .
```

List discoverable workflows or execute a flow directly by name:

```powershell
# List available flows
batautomate list

# Run a flow using Smart Flow Resolver
batautomate run rpachallenge
```

---

## License

This project is licensed under the terms of the Open Source [MIT License](LICENSE).
