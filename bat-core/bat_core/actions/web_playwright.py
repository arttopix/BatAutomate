from typing import Any, Dict
from .base import BaseAction
from .registry import register_action
from ..models.context import ExecutionContext


@register_action("web.open")
class WebOpenAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        url = parameters.get("url")
        headless = parameters.get("headless", True)
        return {"action": "web.open", "url": url, "headless": headless, "status": "simulated"}


@register_action("web.click")
class WebClickAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        selector = parameters.get("selector")
        return {"action": "web.click", "selector": selector, "status": "simulated"}


@register_action("web.type")
class WebTypeAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        selector = parameters.get("selector")
        text = parameters.get("text")
        return {"action": "web.type", "selector": selector, "text": text, "status": "simulated"}
