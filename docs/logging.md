# Structured Logging & Telemetry Standards

This document describes BAT Automate's structured logging architecture, directory partitioning, exception classification, and telemetry data schema.

---

## 1. Directory Structure & Partitioning

BAT Automate records every workflow execution into **Structured JSON Logs** organized by flow name and execution date:

```text
logs/
├── rpa_challenge_solver/               # Partitioned by Flow Name
│   └── 2026-09-11/                     # Partitioned by Execution Date (YYYY-MM-DD)
│       ├── 213906_failed.json          # Format: [HHMMSS]_[status].json
│       └── 213938_success.json
└── invoice_tax_filing/
    └── 2026-09-12/
        ├── 083000_success.json
        └── 091500_failed.json
```

### Key Benefits:
- **Instant Triage:** Log filenames immediately show the execution time and status (`_success` or `_failed`), allowing developers and operations teams to spot failures without opening files.
- **Smart Directory Resolution:** Regardless of the Current Working Directory (CWD) from which a command is executed, `resolve_log_dir` automatically locates the project root and writes logs centrally to `<project_root>/logs/`.

---

## 2. JSON Log Schema Highlights

Each execution log contains comprehensive runtime and business data:

```json
{
  "flow_name": "RPA Challenge Solver",
  "start_time": "2026-09-11T21:39:34.000",
  "end_time": "2026-09-11T21:39:42.869",
  "is_completed": true,
  "has_error": false,
  "metrics": {
    "total_steps": 87,
    "successful_steps": 87,
    "failed_steps": 0,
    "skipped_steps": 0,
    "total_duration_seconds": 4.48,
    "hours_saved": 0.15
  },
  "variables": {
    "target_url": "https://rpachallenge.com/",
    "excel_path": "./assets/challenge.xlsx",
    "screenshot_path": "./assets/result_rpachallenge.png"
  },
  "step_results": [
    {
      "step_id": "step_1",
      "step_name": "Open RPA Challenge Webpage",
      "status": "success",
      "duration_seconds": 0.45,
      "output": null
    }
  ]
}
```

### Privacy & State Sanitization
Internal runtime objects (such as Playwright browser handles, page pointers, and database connections prefixed with `__`) are automatically filtered out prior to JSON serialization, ensuring clean, serializable log files without leaking sensitive memory objects.

---

## 3. Exception Classification Standards

To distinguish operational issues from data problems, errors are categorized into two types:

### 3.1 Technical Exceptions
- **Examples:** Network timeouts, web service down, selector not found after retries, missing driver binary.
- **Responsible Party:** RPA Developer / DevOps Team.
- **Handling:** Trigger technical alert, capture screenshot, retry logic.

### 3.2 Business Exceptions
- **Examples:** Invoice total does not match PO, required Excel column is blank, customer account status is suspended.
- **Responsible Party:** Business Operations / Department Lead.
- **Handling:** Flag transaction for human review, send business alert (e.g. LINE / Teams notification).

---

## 4. Local AI & LLM Readiness

The structured JSON log serves as clean telemetry input for on-device Small Language Models (SLMs) running locally on CPU (e.g. Qwen 2.5):

- When a step fails, the error block, selector context, and recent variable state can be provided directly to a local SLM.
- The SLM generates a plain-language root-cause explanation and suggested fix without requiring any external cloud API tokens.
