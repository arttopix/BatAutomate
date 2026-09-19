# Recommendations for BAT Automate

This document prioritizes the work needed to turn the current prototype into a safer and more dependable RPA platform. The recommended order is to strengthen the existing runtime first, then build interactive and distributed capabilities on top of it.

## 1. Restrict BAT Studio file paths and CORS

### Current concern

BAT Studio accepts a client-supplied `path` for reading and saving flows. The API currently permits absolute paths and paths that resolve outside the workspace. Its CORS configuration also permits every origin.

If the server is reachable by another device, or a user visits an untrusted web page while Studio is running, this could allow that page to request reads or writes to files accessible to the Studio process.

### Recommendation

- Accept paths only within the configured workspace's `flows/` directory.
- Resolve every supplied path and confirm that it remains a descendant of that allowed root before reading or writing.
- Reject absolute paths and traversal attempts such as `../`.
- Limit CORS to the actual development frontend origin, such as `http://localhost:5173`; when FastAPI serves the built frontend itself, prefer same-origin requests and no permissive CORS policy.
- If Studio will listen beyond localhost, add authentication and CSRF protection before exposing write endpoints.

## 2. Implement retry and fallback error handling

### Current concern

The flow schema exposes `on_error`, `max_retries`, `retry_interval`, and `fallback_step_id`. The interpreter currently implements `continue`, but `retry` and `fallback_step_id` have no runtime behavior.

This mismatch makes a declarative flow look more fault tolerant than it actually is.

### Recommendation

- Implement `retry` with deterministic retry count, delay, structured logging, and the final failure attached to the step result.
- Define and document whether `max_retries: 3` means three extra attempts after the original attempt (recommended) or three attempts total.
- Implement `fallback_step_id` as an explicit recovery path, validate that the referenced step exists, and record the handoff in execution telemetry.
- Decide and document the post-fallback behavior. A practical default is to continue with the next normal step after a successful fallback; do not silently retry the failed step unless the flow explicitly requests it.
- Add unit tests for successful retry, exhausted retry, fallback success, missing fallback target, and interactions with `continue`.

## 3. Add continuous integration

### Current concern

The repository has 43 test functions across Core, Worker, and Studio, but test execution currently depends on each developer's local environment. The README also describes an outdated test total.

### Recommendation

Create a GitHub Actions workflow that runs on pull requests and pushes:

- Test supported Python versions (at least 3.10 and the current supported version).
- Install `bat-core`, `bat-worker`, and `bat-studio` with their development dependencies.
- Run the complete pytest suite.
- Build the Studio frontend using `npm ci` and `npm run build`.
- Optionally add formatting, linting, type checking, dependency vulnerability checks, and JSON/schema validation as the project matures.

Update the README so its test status reflects CI rather than a hard-coded passing-test count.

## 4. Build persistent Studio sessions and debugging

### Goal

Once the execution engine is reliable, improve authoring and diagnosis without making ordinary flows depend on Studio.

### Recommended scope

- Maintain a Playwright browser and context per explicit Studio session.
- Add a `run this step` API that executes against the retained browser state.
- Stream interpreter events for step state, logs, errors, variable snapshots, and screenshots.
- Add breakpoints and an element picker that returns robust selector candidates.
- Define session ownership, expiration, cleanup, and isolation so that sessions do not leak browser processes or interfere with one another.

## 5. Build the Worker WebSocket protocol and Orchestrator

### Goal

Move from a single-machine CLI runner to controlled, multi-worker unattended execution.

### Recommended scope

```text
Orchestrator -> dispatches versioned job bundles -> Worker WebSocket -> bat-core executes flow
                                                           |
                                                           +-> status, logs, metrics, screenshots
                                                                    returned to Orchestrator
```

- Authenticate workers and authorize job delivery.
- Require job acknowledgement and use idempotency keys to prevent duplicate execution after reconnects.
- Support reconnects, cancellation, timeouts, heartbeat/health reporting, and clear job state transitions.
- Package and version flow bundles so a worker runs the intended immutable artifact.
- Upload execution artifacts safely and retain structured audit logs.

## Suggested delivery order

1. Studio path containment and CORS restrictions.
2. Retry and fallback runtime behavior with tests.
3. CI for Python tests and the frontend build.
4. Persistent Studio sessions, single-step execution, and telemetry.
5. Worker WebSocket protocol and Orchestrator.

This order establishes safety, predictable runtime behavior, and repeatable verification before expanding into browser-state management and distributed execution.
