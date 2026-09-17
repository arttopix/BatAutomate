import json
import shutil
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from batstudio.server import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "bat-studio"


def test_list_actions():
    response = client.get("/api/actions")
    assert response.status_code == 200
    data = response.json()
    assert "actions" in data
    action_types = [a["type"] for a in data["actions"]]
    assert "web.open" in action_types
    assert "excel.read" in action_types
    assert "ai.prompt" in action_types


def test_list_flows():
    response = client.get("/api/flows")
    assert response.status_code == 200
    flows = response.json()
    assert isinstance(flows, list)
    flow_names = [f["name"] for f in flows]
    assert "RPA Challenge Solver" in flow_names


def test_get_rpachallenge_flow():
    response = client.get("/api/flow", params={"path": "flows/benchmarks/rpachallenge"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["flow"]["name"] == "RPA Challenge Solver"
    assert len(data["flow"]["steps"]) >= 4
    # Verify associated config was loaded
    assert "website" in data["config"]


def test_update_flow_validation_failure():
    # Attempting to save an invalid flow with a step missing required fields ('action' and 'name')
    bad_payload = {
        "path": "flows/benchmarks/non_existent_flow.json",
        "flow": {
            "name": "Broken Flow",
            "steps": [
                {
                    "id": "step_1"
                    # Missing required fields: 'name' and 'action'
                }
            ]
        }
    }
    response = client.put("/api/flow", json=bad_payload)
    # Pydantic validation error should return 422
    assert response.status_code == 422


def test_save_and_update_step_isolated():
    # Test saving and updating steps using a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_flow = Path(tmpdir) / "test_flow.json"
        initial_flow = {
            "name": "Test Flow",
            "description": "Temporary flow for testing",
            "version": "1.0.0",
            "variables": {},
            "steps": [
                {
                    "id": "step_1",
                    "name": "Initial Step",
                    "action": "web.open",
                    "parameters": {"url": "https://example.com"}
                }
            ]
        }
        tmp_flow.write_text(json.dumps(initial_flow), encoding="utf-8")

        # 1. Update single step via PUT /api/flow/step
        updated_step = {
            "id": "step_1",
            "name": "Modified Step",
            "action": "web.open",
            "parameters": {"url": "https://rpachallenge.com", "headless": True}
        }
        step_resp = client.put("/api/flow/step", json={
            "path": str(tmp_flow),
            "step_id": "step_1",
            "step": updated_step
        })
        assert step_resp.status_code == 200

        # Verify disk updated
        disk_data = json.loads(tmp_flow.read_text(encoding="utf-8"))
        assert disk_data["steps"][0]["name"] == "Modified Step"
        assert disk_data["steps"][0]["parameters"]["url"] == "https://rpachallenge.com"

        # 2. Update whole flow via PUT /api/flow
        disk_data["name"] = "Renamed Flow"
        save_resp = client.put("/api/flow", json={
            "path": str(tmp_flow),
            "flow": disk_data
        })
        assert save_resp.status_code == 200

        reloaded = json.loads(tmp_flow.read_text(encoding="utf-8"))
        assert reloaded["name"] == "Renamed Flow"
