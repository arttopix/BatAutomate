import time
from typing import Any, Dict

from .base import BaseAction
from .registry import register_action
from ..models.context import ExecutionContext


@register_action("logic.set_variable")
class SetVariableAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        name = parameters.get("name")
        value = parameters.get("value")
        if name:
            context.set_variable(name, value)
        return value


@register_action("logic.delay")
class DelayAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        seconds = float(parameters.get("seconds", 1.0))
        time.sleep(seconds)
        return {"delayed_seconds": seconds}
