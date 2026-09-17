# BAT Studio

The Developer Studio, Step Inspector, and Live Debugger for **BAT Automate**.

---

## 1. Vision & Core Philosophy

In traditional RPA platforms, workflow authoring relies heavily on tedious visual node-dragging (drag-and-drop canvases), which often results in messy "spaghetti node" diagrams and high development overhead. 

With the emergence of modern AI and Large Language Models, developers no longer need to manually drag 50 boxes to build a workflow. Instead, **BAT Studio** is designed around an **AI-Assisted, Developer-First Paradigm**:

- **AI-Accelerated Flow Authoring:** Plain-text prompt bar generates or updates `flow.json` workflows in seconds.
- **Linear Step Timeline:** Clean, vertical sequence of steps (like Postman or GitHub Actions) rather than complex 2D wire-connecting graphs.
- **Precision Element Inspector:** Point-and-click overlay on live browser pages to capture robust, multi-layer selectors (Role/Text, CSS, XPath).
- **Persistent Session & "Run Only This Step":** Keep browser contexts open in memory to test and tune individual step selectors in sub-second feedback loops without restarting flows from step 1.
- **Root-Cause Traceability:** Instant error diagnosis pairing failed steps with runtime variable snapshots and millisecond-accurate error screenshots.
- **Zero Heavy Electron Bloat:** Built as a modern Single-Page Application (SPA) powered by a lightweight FastAPI Python backend and a blazing-fast React/TypeScript frontend.

---

## 2. System Architecture & Tech Stack

BAT Studio operates as an interactive development layer running locally on the developer's PC, directly communicating with `bat-core`:

```text
+-------------------------------------------------------------------------+
|                        BAT Studio (Frontend SPA)                        |
|             React 18/19 + TypeScript + Vite + Tailwind CSS             |
|                                                                         |
|  [ AI Prompt Bar ]  [ Steps Timeline ]  [ Inspector ]  [ Live Debugger ] |
+-----------------------------------+-------------------------------------+
                                    |
                         REST APIs & WebSockets
                                    |
+-----------------------------------+-------------------------------------+
|                      BAT Studio Server (Backend)                        |
|                  FastAPI + WebSocket Event Hub                          |
+-----------------------------------+-------------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
+-----------------------+                       +-----------------------+
|       BAT Core        |                       |   Playwright Engine   |
| Flow Engine & Actions |                       | Persistent Context &  |
| (Interpreter, Models) |                       | Element Picker Hook   |
+-----------------------+                       +-----------------------+
```

### Technology Selection

| Tier | Technology | Purpose & Rationale |
| :--- | :--- | :--- |
| **Backend Engine** | **FastAPI (Python 3.10+)** | Native async runtime, bi-directional WebSockets, and zero-friction integration with `bat-core` Pydantic models. |
| **Frontend Framework** | **React + Vite (TypeScript)** | Industry-standard developer experience, fast Hot Module Replacement (HMR), and strict type safety for flow definitions. |
| **Styling & UI Kit** | **Tailwind CSS + shadcn/ui** | Modern, accessible dark-mode UI components (Tabs, Collapsibles, Dialogs, Badges) tailored for developer tools. |
| **Panel Management** | **`react-resizable-panels`** | Smooth, collapsible multi-column layout for customizable workspace widths. |
| **Code & Expression Editor** | **`@monaco-editor/react`** | Embedded VS Code editor for syntax-highlighted JSON editing and dynamic expression preview (`${var.prop}`). |
| **Browser Controller** | **Playwright Persistent Context** | Live DOM inspection, screenshot streaming, and isolated single-step execution. |

---

## 3. UI Workspace Composition (3-Column Layout)

BAT Studio organizes the developer experience into three coordinated panels:

```text
+----------------------------------------------------------------------------------------------------+
| Top Bar: [Flow: rpachallenge] [Env: staging v]  [ > Run All ]  [ || Debug Step ]  [ Reset Session ]|
+------------------------------------+--------------------------------+------------------------------+
| 1. Step Timeline (Left)            | 2. Step Inspector (Center)     | 3. Live Debugger (Right)     |
|                                    |                                |                              |
| - Vertical execution order         | - Dynamic action parameter     | - Live Variable Pool         |
| - Status pills (Pending, Running,  |   form (Schema-driven)         |   (${config}, ${vars})       |
|   Success, Failed)                 | - Multi-layer Selector Picker  | - Real-time execution logs   |
| - Breakpoint toggling              |   ([Pick from Page] [Test])    | - Error screenshot viewer    |
| - Drag-to-reorder steps            | - Timeout & retry tuning       | - Local AI root-cause        |
| - Add step via AI prompt           | - [ Run Only This Step ]       |   diagnosis and quick-fix    |
+------------------------------------+--------------------------------+------------------------------+
```

### Key Workflow Capabilities
1. **Interactive Element Picker:** Clicking `[ Pick from Page ]` overlays a visual crosshair on the active Playwright browser. Clicking any element automatically generates and validates candidates:
   - Primary: `role=button[name="Submit"]`
   - Secondary CSS: `button.btn-primary#submit-form`
   - XPath: `//button[@type='submit' and text()='Submit']`
2. **Step-by-Step Interactive Debugging:** Set breakpoints on any step. Step over actions one at a time while observing variables mutate live in the right-hand panel.
3. **Isolated Action Execution:** Tweak a selector or timeout in the inspector and immediately execute only that step against the running browser session without resetting state.
4. **Environment Configuration Switcher:** Toggle between `dev`, `staging`, and `production` to dynamically load corresponding `config.json` files and test environment overrides.

---

## 4. Proposed Directory Layout

```text
bat-studio/
├── README.md                           # Architecture and development plan (this file)
├── pyproject.toml                      # Python package configuration (CLI entry point: batstudio)
├── batstudio/                          # Python backend service
│   ├── __init__.py                     # Package metadata
│   ├── cli.py                          # CLI runner (e.g., `batstudio run flows/my_flow`)
│   ├── server.py                       # FastAPI application & REST routing
│   ├── websocket.py                    # Bi-directional WebSocket event dispatcher
│   ├── session.py                      # Persistent browser & flow execution session manager
│   └── picker.py                       # Playwright element inspection & selector generator
└── frontend/                           # React + TypeScript single-page application
    ├── package.json                    # Node dependencies (Vite, React, Tailwind, Lucide)
    ├── vite.config.ts                  # Vite build and proxy configuration
    ├── tsconfig.json                   # TypeScript compiler options
    ├── tailwind.config.js              # Tailwind styling configuration
    ├── index.html                      # SPA entry point
    └── src/
        ├── main.tsx                    # React application bootstrap
        ├── App.tsx                     # Main layout shell with resizable 3 columns
        ├── components/
        │   ├── Header.tsx              # Top bar, flow selector, run/debug toolbar
        │   ├── AiPromptBar.tsx         # Natural-language flow generation & modification
        │   ├── StepsTimeline.tsx       # Vertical step sequence, reordering, breakpoints
        │   ├── StepInspector.tsx       # Schema-driven action parameter form
        │   ├── ElementPickerModal.tsx  # Browser element selector dialog & test runner
        │   ├── VariableWatcher.tsx     # Dynamic runtime variable context inspector
        │   └── LogViewer.tsx           # Real-time WebSocket log streamer & screenshot viewer
        ├── hooks/
        │   ├── useWebSocket.ts         # WebSocket state synchronization hook
        │   └── useFlow.ts              # Flow state management hook
        ├── types/
        │   ├── flow.ts                 # Flow schema and action type definitions
        │   └── session.ts              # Execution session and telemetry interfaces
        └── lib/
            ├── api.ts                  # Axios / Fetch client for studio backend
            └── utils.ts                # Formatting and class merging helpers
```

---

## 5. Development Roadmap & Milestones

### Milestone 1: Backend Foundation & Project Scaffolding
- [ ] Initialize `bat-studio/pyproject.toml` with FastAPI, Uvicorn, and `bat-core` dependency.
- [ ] Implement `batstudio` CLI command that serves FastAPI on `http://localhost:8080`.
- [ ] Implement REST endpoints:
  - `GET /api/flows`: Discover and list flows across the workspace.
  - `GET /api/flows/{flow_id}`: Fetch flow JSON definition and configuration.
  - `POST /api/flows/{flow_id}`: Save updated flow JSON with schema validation.
  - `GET /api/actions`: Export available action registry metadata and schemas from `bat-core`.

### Milestone 2: Frontend Foundation & Resizable 3-Column Shell
- [ ] Initialize Vite + React + TypeScript in `bat-studio/frontend/`.
- [ ] Configure Tailwind CSS and dark-mode color scheme.
- [ ] Implement resizable 3-column layout using `react-resizable-panels`.
- [ ] Build Top Bar with flow selector, environment switcher, and run toolbar.

### Milestone 3: Step Timeline & Schema-Driven Inspector
- [ ] Implement `StepsTimeline` rendering sequential steps with icons, names, and status badges.
- [ ] Implement `StepInspector` generating dynamic form inputs according to the action schema:
  - Text fields for `selector`, `url`, `timeout`, `value`.
  - Autocomplete suggestion for dynamic variables (`${config.*}`, `${vars.*}`).
- [ ] Bi-directional state binding: Updates in inspector immediately reflect in the underlying `flow.json`.

### Milestone 4: Persistent Browser Session & Single-Step Execution
- [ ] Implement `session.py` backend service maintaining persistent Playwright browser instances.
- [ ] Implement `POST /api/session/step`: Execute a single isolated step in the active browser context.
- [ ] Implement `ElementPicker` hook: Inject DOM highlight crosshair and return robust selector candidates.

### Milestone 5: Live Debugger & Real-Time Telemetry
- [ ] Implement WebSocket connection streaming real-time execution events from `FlowInterpreter`.
- [ ] Visual step progression: Highlight active step, success (green), and failure (red).
- [ ] Implement `VariableWatcher` displaying runtime variables in real time.
- [ ] Implement Error Telemetry: Instant modal showing error details and millisecond-accurate failure screenshots.

### Milestone 6: AI Prompt Bar & Bundle Packaging
- [ ] Implement `AiPromptBar` connecting to local Ollama (`ai.prompt`) to generate or modify step definitions from natural language.
- [ ] Implement Project Bundle Exporter: Package flow definitions, configurations, and assets into standalone archives ready for `bat-worker`.
