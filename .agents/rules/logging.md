# Logging Architecture & Business Telemetry

This document outlines the logging standards, structured log formats, and business metrics recording for **BAT Automate**.

---

## 1. Structured JSON Execution Logs

1. **Automatic Generation:**
   - Every execution run must generate a structured JSON log file in the `logs/` directory named `log_YYYYMMDD_HHMMSS.json`.
2. **Variable Sanitization:**
   - Filter out internal system variables (variables starting with `__*`) from public log outputs to maintain clean, readable audit trails.
3. **Execution Record Structure:**
   - Each log file must record: flow metadata, overall status, start/end timestamps, duration, step-by-step execution details, and business summary metrics.

---

## 2. Business-Oriented Telemetry

Logging must not be restricted to technical execution data. It must capture business impact indicators:
- **Transaction Counts:** Total items processed, items succeeded, business exceptions, technical failures.
- **Time Saved:** Calculated duration saved compared to manual human execution.
- **Cost Saved:** Estimated financial savings based on business configuration.

---

## 3. Real-Time Streaming & AI Integration Roadmap

- **WebSocket Streaming (Phase 3 - Orchestrator):** Worker instances stream log packets over WebSocket to the central Orchestrator for real-time dashboard updates and PostgreSQL archiving.
- **Automated SLM Error Diagnosis:** When a failure occurs, the structured JSON failure block is handed off to a local SLM instance to synthesize an actionable business-language summary sent directly to LINE notifications.
