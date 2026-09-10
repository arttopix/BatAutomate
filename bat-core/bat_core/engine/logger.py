import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.context import ExecutionContext, StepResult


class ExecutionLogger:
    """
    Structured logger for recording flow execution steps and metrics.
    Prints to console and outputs structured JSON logs.
    """

    def __init__(self, log_dir: Optional[str] = None):
        self.logger = logging.getLogger("bat_core")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.log_dir = Path(log_dir) if log_dir else None
        if self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_step_start(self, step_id: str, step_name: str, action: str) -> None:
        self.logger.info(f"Starting Step [{step_id}] '{step_name}' (Action: {action})")

    def log_step_result(self, result: StepResult) -> None:
        status_upper = result.status.upper()
        if result.status == "success":
            self.logger.info(
                f"Completed Step [{result.step_id}] '{result.step_name}' in {result.duration_seconds:.3f}s"
            )
        elif result.status == "failed":
            self.logger.error(
                f"Failed Step [{result.step_id}] '{result.step_name}' - [{result.error_type} Error]: {result.error_message}"
            )
        else:
            self.logger.warning(f"Skipped Step [{result.step_id}] '{result.step_name}'")

    def log_execution_summary(self, context: ExecutionContext) -> None:
        m = context.metrics
        self.logger.info("=== Flow Execution Summary ===")
        self.logger.info(f"Flow Name: {context.flow_name}")
        self.logger.info(f"Total Steps: {m.total_steps} (Success: {m.successful_steps}, Failed: {m.failed_steps}, Skipped: {m.skipped_steps})")
        self.logger.info(f"Total Duration: {m.total_duration_seconds:.2f}s")

        if self.log_dir:
            log_file = self.log_dir / f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            log_file.write_text(json.dumps(context.model_dump(mode="json"), indent=2), encoding="utf-8")
            self.logger.info(f"Saved JSON log to: {log_file}")
