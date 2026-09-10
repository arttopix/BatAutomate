from pathlib import Path
from typing import Any, Dict
import pandas as pd

from .base import BaseAction
from .registry import register_action
from ..models.context import ExecutionContext


@register_action("excel.read")
class ExcelReadAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        file_path = parameters.get("file_path")
        sheet_name = parameters.get("sheet_name", 0)
        
        if not file_path or not Path(file_path).exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        df = pd.read_excel(file_path, sheet_name=sheet_name)
        records = df.to_dict(orient="records")
        return records


@register_action("excel.write")
class ExcelWriteAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        file_path = parameters.get("file_path")
        data = parameters.get("data", [])
        sheet_name = parameters.get("sheet_name", "Sheet1")

        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            raise ValueError("Data for excel.write must be a list of dicts or a dict.")

        df.to_excel(file_path, sheet_name=sheet_name, index=False)
        return {"rows_written": len(df), "file_path": file_path}
