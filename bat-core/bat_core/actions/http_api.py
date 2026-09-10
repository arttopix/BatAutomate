from typing import Any, Dict
import requests

from .base import BaseAction
from .registry import register_action
from ..models.context import ExecutionContext


@register_action("http.request")
class HttpRequestAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        url = parameters.get("url")
        method = parameters.get("method", "GET").upper()
        headers = parameters.get("headers", {})
        payload = parameters.get("payload")
        timeout = parameters.get("timeout", 30)

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=payload if isinstance(payload, dict) else None,
            data=payload if isinstance(payload, str) else None,
            timeout=timeout
        )

        try:
            body = response.json()
        except Exception:
            body = response.text

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": body
        }
