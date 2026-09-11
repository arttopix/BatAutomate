from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VariableDefinition(BaseModel):
    name: str
    value: Any
    description: Optional[str] = None


class ErrorHandlerConfig(BaseModel):
    on_error: str = "stop"  # stop, continue, retry
    max_retries: int = 0
    retry_interval: float = 1.0
    fallback_step_id: Optional[str] = None


class Step(BaseModel):
    id: str
    name: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    output_var: Optional[str] = None
    sub_steps: Optional[List["Step"]] = None
    error_handler: Optional[ErrorHandlerConfig] = None
    condition: Optional[str] = None


Step.model_rebuild()


class ActionConfig(BaseModel):
    name: str
    action_class: str
    module: str
    description: Optional[str] = None


class FlowDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    variables: Dict[str, Any] = Field(default_factory=dict)
    steps: List[Step] = Field(default_factory=list)
