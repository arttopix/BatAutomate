import json
from pathlib import Path
import pytest
from batautomate.models.flow import FlowDefinition, Step
from batautomate.engine.interpreter import FlowInterpreter
from batautomate.engine.evaluator import VariableEvaluator


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
    from batautomate.models.context import ExecutionContext
    from batautomate.engine.logger import ExecutionLogger

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


def test_resolve_log_dir(tmp_path):
    from batautomate.engine.logger import resolve_log_dir

    # 1. Custom log dir explicitly specified
    custom = resolve_log_dir(str(tmp_path / "my_logs"))
    assert custom == (tmp_path / "my_logs").resolve()

    # 2. Inside project structure (containing .git or bat-core)
    # The current repo has root at BatAutomate
    resolved = resolve_log_dir()
    assert (resolved.parent / "bat-core").exists() or (resolved.parent / ".git").exists()
    assert resolved.name == "logs"


def test_logic_if_action():
    # 1. True condition
    flow_true = FlowDefinition(
        name="Test If True",
        variables={"role": "Programmer", "result": "initial"},
        steps=[
            Step(
                id="step_check",
                name="Check Role",
                action="logic.if",
                parameters={
                    "left": "${role}",
                    "operator": "equals",
                    "right": "Programmer"
                },
                sub_steps=[
                    Step(
                        id="sub_set",
                        name="Set Success",
                        action="logic.set_variable",
                        parameters={"name": "result", "value": "is_programmer"},
                        output_var="result"
                    )
                ]
            )
        ]
    )

    interpreter = FlowInterpreter()
    ctx_true = interpreter.run_flow(flow_true)
    assert ctx_true.get_variable("result") == "is_programmer"
    assert ctx_true.step_results[0].status == "success"

    # 2. False condition
    flow_false = FlowDefinition(
        name="Test If False",
        variables={"role": "Manager", "result": "initial"},
        steps=[
            Step(
                id="step_check",
                name="Check Role",
                action="logic.if",
                parameters={
                    "left": "${role}",
                    "operator": "equals",
                    "right": "Programmer"
                },
                sub_steps=[
                    Step(
                        id="sub_set",
                        name="Set Success",
                        action="logic.set_variable",
                        parameters={"name": "result", "value": "is_programmer"},
                        output_var="result"
                    )
                ]
            )
        ]
    )

    ctx_false = interpreter.run_flow(flow_false)
    assert ctx_false.get_variable("result") == "initial"
    assert ctx_false.step_results[0].status == "skipped"


def test_step_condition():
    flow = FlowDefinition(
        name="Test Step Condition",
        variables={"role": "Manager", "result": "initial"},
        steps=[
            Step(
                id="step_skip",
                name="Skip If Not Programmer",
                action="logic.set_variable",
                condition="${role} == Programmer",
                parameters={"name": "result", "value": "modified"},
                output_var="result"
            )
        ]
    )

    interpreter = FlowInterpreter()
    ctx = interpreter.run_flow(flow)
    assert ctx.get_variable("result") == "initial"
    assert ctx.step_results[0].status == "skipped"


def test_logic_if_else_and_append():
    flow = FlowDefinition(
        name="Test If Else and Append",
        variables={"role": "Analyst", "name": "John", "skipped": []},
        steps=[
            Step(
                id="step_check",
                name="Check Role",
                action="logic.if",
                parameters={
                    "left": "${role}",
                    "operator": "equals",
                    "right": "Programmer"
                },
                sub_steps=[
                    Step(
                        id="sub_pos",
                        name="Set Processed",
                        action="logic.set_variable",
                        parameters={"name": "status", "value": "processed"}
                    )
                ],
                else_steps=[
                    Step(
                        id="sub_else_append",
                        name="Record Non-Programmer",
                        action="logic.append",
                        parameters={
                            "target": "skipped",
                            "item": {
                                "First Name": "${name}",
                                "Role": "${role}"
                            }
                        }
                    )
                ]
            )
        ]
    )

    interpreter = FlowInterpreter()
    ctx = interpreter.run_flow(flow)

    assert ctx.is_completed is True
    assert ctx.has_error is False
    assert ctx.get_variable("status") is None
    skipped = ctx.get_variable("skipped")
    assert isinstance(skipped, list)
    assert len(skipped) == 1
    assert skipped[0] == {"First Name": "John", "Role": "Analyst"}
    check_result = next(r for r in ctx.step_results if r.step_id == "step_check")
    assert check_result.status == "success"
    assert check_result.output["branch_executed"] == "else"


def test_flow_failure_diagnosis():
    flow = FlowDefinition(
        name="Test Failing Flow",
        steps=[
            Step(
                id="step_fail_file",
                name="Read Missing File",
                action="excel.read",
                parameters={"file_path": "non_existent_file.xlsx"}
            )
        ]
    )

    interpreter = FlowInterpreter()
    ctx = interpreter.run_flow(flow)

    assert ctx.is_completed is False
    assert ctx.has_error is True
    assert ctx.failure_details is not None
    assert ctx.failure_details.failed_step_id == "step_fail_file"
    assert ctx.failure_details.failed_step_name == "Read Missing File"
    assert ctx.failure_details.action == "excel.read"
    assert ctx.failure_details.exception_class == "FileNotFoundError"
    assert "not found" in ctx.failure_details.root_cause.lower()
    assert len(ctx.failure_details.suggested_fix) > 0




