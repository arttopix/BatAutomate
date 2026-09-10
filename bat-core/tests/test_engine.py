import json
from pathlib import Path
import pytest
from bat_core.models.flow import FlowDefinition, Step
from bat_core.engine.interpreter import FlowInterpreter
from bat_core.engine.evaluator import VariableEvaluator


def test_variable_evaluator():
    vars_ctx = {"name": "BAT", "details": {"version": "1.0"}}
    val = VariableEvaluator.evaluate_value("Hello ${name} v${details.version}", vars_ctx)
    assert val == "Hello BAT v1.0"


def test_interpreter_basic_run():
    flow = FlowDefinition(
        name="Test Flow",
        variables={"msg": "hello"},
        steps=[
            Step(
                id="s1",
                name="Set Variable",
                action="logic.set_variable",
                parameters={"name": "res", "value": "${msg}_world"},
                output_var="res"
            )
        ]
    )

    interpreter = FlowInterpreter()
    ctx = interpreter.run_flow(flow)

    assert ctx.is_completed is True
    assert ctx.has_error is False
    assert ctx.get_variable("res") == "hello_world"
    assert len(ctx.step_results) == 1
    assert ctx.step_results[0].status == "success"


def test_interpreter_load_sample_flow_json():
    json_path = Path(__file__).parent.parent / "examples" / "sample_flow.json"
    assert json_path.exists()

    content = json_path.read_text(encoding="utf-8")
    raw_json = json.loads(content)
    flow_def = FlowDefinition.model_validate(raw_json)

    interpreter = FlowInterpreter()
    ctx = interpreter.run_flow(flow_def)

    assert ctx.is_completed is True
    assert ctx.has_error is False
    assert len(ctx.step_results) == 3


def test_logger_safe_serialization_with_custom_objects(tmp_path):
    from bat_core.models.context import ExecutionContext
    from bat_core.engine.logger import ExecutionLogger

    class NonSerializableClass:
        def __repr__(self):
            return "<CustomObject>"

    ctx = ExecutionContext(flow_name="Test Safe Serialization")
    ctx.set_variable("__internal_obj__", NonSerializableClass())
    ctx.set_variable("normal_var", 123)
    ctx.set_variable("custom_obj", NonSerializableClass())

    logger = ExecutionLogger(log_dir=str(tmp_path))
    # Should not raise PydanticSerializationError
    logger.log_execution_summary(ctx)

    log_files = list(tmp_path.glob("*/*/*.json"))
    assert len(log_files) == 1
    content = json.loads(log_files[0].read_text(encoding="utf-8"))
    assert "__internal_obj__" not in content["variables"]
    assert content["variables"]["normal_var"] == 123
    assert content["variables"]["custom_obj"] == "<CustomObject>"


