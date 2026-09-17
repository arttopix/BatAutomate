import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from batautomate.actions import ActionRegistry
from batautomate.models.flow import FlowDefinition

app = FastAPI(
    title="BAT Studio API",
    description="Backend service for BAT Studio - Step Inspector, Live Debugger, and Flow Management",
    version="0.1.0a1"
)

# Enable CORS for local development and future frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root():
    """
    Redirect root to Swagger UI documentation.
    """
    return RedirectResponse(url="/docs")


def get_workspace_root() -> Path:
    """
    Finds the root workspace directory by looking for flows/ directory.
    """
    current = Path.cwd().resolve()
    for parent in [current] + list(current.parents):
        if (parent / "flows").is_dir() and (parent / "bat-core").is_dir():
            return parent
    return current


class FlowSummary(BaseModel):
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    path: str
    bundle_dir: str
    steps_count: int
    has_config: bool


class SaveFlowRequest(BaseModel):
    path: str
    flow: Dict[str, Any]


class UpdateStepRequest(BaseModel):
    path: str
    step_id: str
    step: Dict[str, Any]


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "bat-studio",
        "workspace_root": str(get_workspace_root())
    }


@app.get("/api/actions")
def list_actions():
    """
    Lists all available actions registered in bat-core ActionRegistry.
    """
    actions = ActionRegistry.list_actions()
    action_list = []
    for action_type, action_cls in sorted(actions.items()):
        doc = action_cls.__doc__.strip() if action_cls.__doc__ else "No documentation available."
        action_list.append({
            "type": action_type,
            "class_name": action_cls.__name__,
            "module": action_cls.__module__,
            "description": doc.splitlines()[0] if doc else "",
            "docstring": doc
        })
    return {"actions": action_list}


@app.get("/api/flows", response_model=List[FlowSummary])
def list_flows():
    """
    Scans the workspace for all available flow.json files.
    """
    root = get_workspace_root()
    flows_dir = root / "flows"
    if not flows_dir.is_dir():
        return []

    summaries = []
    for flow_path in sorted(flows_dir.glob("**/flow.json")):
        try:
            content = flow_path.read_text(encoding="utf-8")
            data = json.loads(content)
            rel_path = str(flow_path.relative_to(root)).replace("\\", "/")
            bundle_dir = str(flow_path.parent.relative_to(root)).replace("\\", "/")
            has_cfg = (
                (flow_path.parent / "config" / "config.json").is_file()
                or (flow_path.parent / "config.json").is_file()
            )
            summaries.append(
                FlowSummary(
                    name=data.get("name", flow_path.parent.name),
                    description=data.get("description"),
                    version=data.get("version", "1.0.0"),
                    path=rel_path,
                    bundle_dir=bundle_dir,
                    steps_count=len(data.get("steps", [])),
                    has_config=has_cfg
                )
            )
        except Exception:
            continue

    return summaries


@app.get("/api/flow")
def get_flow(path: str = Query(..., description="Relative or absolute path to flow.json")):
    """
    Loads and parses a flow definition and its configuration.
    """
    root = get_workspace_root()
    target_path = Path(path)
    if not target_path.is_absolute():
        target_path = (root / target_path).resolve()

    if target_path.is_dir():
        target_path = target_path / "flow.json"

    if not target_path.is_file():
        raise HTTPException(status_code=404, detail=f"Flow file not found: {path}")

    try:
        raw_text = target_path.read_text(encoding="utf-8")
        flow_data = json.loads(raw_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read flow JSON: {e}")

    # Validate against Pydantic schema
    validation_error = None
    try:
        FlowDefinition(**flow_data)
    except Exception as e:
        validation_error = str(e)

    # Auto-load associated configuration if available
    config_data = {}
    config_file = target_path.parent / "config" / "config.json"
    if not config_file.is_file():
        config_file = target_path.parent / "config.json"
    if config_file.is_file():
        try:
            config_data = json.loads(config_file.read_text(encoding="utf-8"))
        except Exception:
            config_data = {}

    rel_path = str(target_path.relative_to(root)).replace("\\", "/") if target_path.is_relative_to(root) else str(target_path)

    return {
        "path": rel_path,
        "bundle_dir": str(target_path.parent.relative_to(root)).replace("\\", "/") if target_path.parent.is_relative_to(root) else str(target_path.parent),
        "flow": flow_data,
        "config": config_data,
        "is_valid": validation_error is None,
        "validation_error": validation_error
    }


@app.put("/api/flow")
def save_flow(req: SaveFlowRequest):
    """
    Validates and saves an entire flow definition back to disk.
    """
    root = get_workspace_root()
    target_path = Path(req.path)
    if not target_path.is_absolute():
        target_path = (root / target_path).resolve()

    if target_path.is_dir():
        target_path = target_path / "flow.json"

    # Schema validation before saving
    try:
        flow_def = FlowDefinition(**req.flow)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Schema Validation Error: {e}")

    # Preserve schema reference if present in target file
    schema_ref = None
    if target_path.is_file():
        try:
            old_data = json.loads(target_path.read_text(encoding="utf-8"))
            schema_ref = old_data.get("$schema")
        except Exception:
            pass

    save_payload = req.flow.copy()
    if schema_ref and "$schema" not in save_payload:
        save_payload = {"$schema": schema_ref, **save_payload}

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json.dumps(save_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file to disk: {e}")

    rel_path = str(target_path.relative_to(root)).replace("\\", "/") if target_path.is_relative_to(root) else str(target_path)
    return {
        "status": "success",
        "message": f"Flow '{flow_def.name}' saved successfully",
        "path": rel_path
    }


def _update_step_in_list(steps: List[Dict[str, Any]], step_id: str, new_step_data: Dict[str, Any]) -> bool:
    """
    Recursively finds and updates a step in a list of steps (including sub_steps and else_steps).
    """
    for i, s in enumerate(steps):
        if s.get("id") == step_id:
            steps[i] = new_step_data
            return True
        if "sub_steps" in s and isinstance(s["sub_steps"], list):
            if _update_step_in_list(s["sub_steps"], step_id, new_step_data):
                return True
        if "else_steps" in s and isinstance(s["else_steps"], list):
            if _update_step_in_list(s["else_steps"], step_id, new_step_data):
                return True
    return False


@app.put("/api/flow/step")
def update_single_step(req: UpdateStepRequest):
    """
    Updates a single step by its step_id without having to overwrite the whole flow manually.
    """
    root = get_workspace_root()
    target_path = Path(req.path)
    if not target_path.is_absolute():
        target_path = (root / target_path).resolve()

    if target_path.is_dir():
        target_path = target_path / "flow.json"

    if not target_path.is_file():
        raise HTTPException(status_code=404, detail=f"Flow file not found: {req.path}")

    flow_data = json.loads(target_path.read_text(encoding="utf-8"))
    steps = flow_data.get("steps", [])

    updated = _update_step_in_list(steps, req.step_id, req.step)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Step with ID '{req.step_id}' not found in flow")

    # Validate updated flow structure
    try:
        FlowDefinition(**flow_data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Step update resulted in invalid flow: {e}")

    target_path.write_text(json.dumps(flow_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "status": "success",
        "message": f"Step '{req.step_id}' updated successfully",
        "step": req.step
    }
