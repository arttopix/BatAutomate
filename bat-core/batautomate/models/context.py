from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StepResult(BaseModel):
    step_id: str
    step_name: str
    status: str  # success, failed, skipped
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    output: Optional[Any] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None  # Technical, Business


class ExecutionMetrics(BaseModel):
    total_steps: int = 0
    successful_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    total_duration_seconds: float = 0.0
    hours_saved: float = 0.0
    cost_saved: float = 0.0


class ExecutionContext(BaseModel):
    flow_name: str
    start_time: datetime = Field(default_factory=datetime.now)
    variables: Dict[str, Any] = Field(default_factory=dict)
    step_results: List[StepResult] = Field(default_factory=list)
    metrics: ExecutionMetrics = Field(default_factory=ExecutionMetrics)
    is_completed: bool = False
    has_error: bool = False

    def set_variable(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        return self.variables.get(name, default)
