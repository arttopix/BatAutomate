from datetime import datetime
from typing import Any, Dict, Optional

from .evaluator import VariableEvaluator
from .logger import ExecutionLogger
from ..actions.registry import ActionRegistry
from ..models.context import ExecutionContext, StepResult, FailureDetails
from ..models.flow import FlowDefinition, Step


class FlowInterpreter:
    """
    Interpreter that parses FlowDefinition, evaluates expressions, and executes steps sequentially.
    """

    def __init__(self, logger: Optional[ExecutionLogger] = None):
        self.logger = logger or ExecutionLogger()

    def _diagnose_failure(self, step: Step, exc: Exception) -> FailureDetails:
        exc_class = type(exc).__name__
        err_msg = str(exc)
        error_type = "Business" if "Business" in exc_class else "Technical"

        if isinstance(exc, FileNotFoundError) or ("not found" in err_msg.lower() and "file" in err_msg.lower()):
            root_cause = f"Required file was not found during execution of step '{step.name}'."
            suggested_fix = "Verify the target file path exists and that relative paths are correctly anchored to the flow project directory."
        elif "timeout" in err_msg.lower() or "waiting for" in err_msg.lower():
            root_cause = f"Operation timed out waiting for element or network response in step '{step.name}' (Action: {step.action})."
            suggested_fix = "Verify target web page/API is reachable, inspect selector validity, or increase action timeout parameter."
        elif "locator" in err_msg.lower() or "strict mode violation" in err_msg.lower() or "selector" in err_msg.lower():
            root_cause = f"Web element could not be uniquely located on page in step '{step.name}'."
            suggested_fix = "Check DOM changes on target page and update selector/label to be more resilient."
        elif isinstance(exc, KeyError):
            root_cause = f"Referenced variable or key {err_msg} is missing from execution context."
            suggested_fix = "Ensure preceding steps initialize this variable or verify variable expression spelling."
        else:
            root_cause = f"Unhandled {exc_class} in step '{step.name}' ({step.action}): {err_msg}"
            suggested_fix = f"Inspect input parameters to step '{step.id}' ({step.action}) and verify prerequisite conditions."

        return FailureDetails(
            failed_step_id=step.id,
            failed_step_name=step.name,
            action=step.action,
            error_type=error_type,
            exception_class=exc_class,
            error_message=err_msg,
            root_cause=root_cause,
            suggested_fix=suggested_fix
        )

    def run_flow(self, flow_def: FlowDefinition, initial_vars: Optional[Dict[str, Any]] = None) -> ExecutionContext:
        context = ExecutionContext(flow_name=flow_def.name)

        if flow_def.variables:
            for k, v in flow_def.variables.items():
                context.set_variable(k, v)

        if initial_vars:
            for k, v in initial_vars.items():
                context.set_variable(k, v)

        start_time = datetime.now()

        try:
            for step in flow_def.steps:
                self._execute_step(step, context)
            context.is_completed = True
        except Exception as e:
            context.has_error = True
            self.logger.logger.error(f"Flow execution failed with unhandled exception: {str(e)}")

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        context.metrics.total_steps = len(context.step_results)
        context.metrics.successful_steps = sum(1 for r in context.step_results if r.status == "success")
        context.metrics.failed_steps = sum(1 for r in context.step_results if r.status == "failed")
        context.metrics.skipped_steps = sum(1 for r in context.step_results if r.status == "skipped")
        context.metrics.total_duration_seconds = total_duration

        self.logger.log_execution_summary(context)
        return context

    def _execute_step(self, step: Step, context: ExecutionContext) -> None:
        self.logger.log_step_start(step.id, step.name, step.action)
        start_time = datetime.now()

        evaluated_params = VariableEvaluator.evaluate_value(step.parameters, context.variables)

        if step.condition:
            eval_cond = VariableEvaluator.evaluate_value(step.condition, context.variables)
            if not self._evaluate_condition_expr(eval_cond):
                result = StepResult(
                    step_id=step.id,
                    step_name=step.name,
                    status="skipped",
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration_seconds=0.0,
                    output={"skipped_reason": f"Condition '{step.condition}' not met"}
                )
                context.step_results.append(result)
                self.logger.log_step_result(result)
                return

        if step.action == "logic.loop":
            self._handle_loop_step(step, evaluated_params, context, start_time)
            return

        if step.action == "logic.if":
            self._handle_if_step(step, evaluated_params, context, start_time)
            return

        try:
            action_cls = ActionRegistry.get(step.action)
            action_instance = action_cls()
            output = action_instance.execute(evaluated_params, context)

            if step.output_var and output is not None:
                context.set_variable(step.output_var, output)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            result = StepResult(
                step_id=step.id,
                step_name=step.name,
                action=step.action,
                status="success",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                output=output
            )
            context.step_results.append(result)
            self.logger.log_step_result(result)

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            failure_diag = self._diagnose_failure(step, e)

            result = StepResult(
                step_id=step.id,
                step_name=step.name,
                action=step.action,
                status="failed",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                error_message=str(e),
                error_type=failure_diag.error_type
            )
            context.step_results.append(result)
            self.logger.log_step_result(result)

            if context.failure_details is None:
                context.failure_details = failure_diag

            if step.error_handler and step.error_handler.on_error == "continue":
                return
            raise e

    def _handle_loop_step(self, step: Step, evaluated_params: Dict[str, Any], context: ExecutionContext, start_time: datetime) -> None:
        items = evaluated_params.get("items", [])
        item_var = evaluated_params.get("item_var", "item")
        sub_steps = step.sub_steps or []

        if not isinstance(items, list):
            items = [items]

        for index, item in enumerate(items):
            context.set_variable(item_var, item)
            context.set_variable(f"{item_var}_index", index)
            for sub_step in sub_steps:
                self._execute_step(sub_step, context)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = StepResult(
            step_id=step.id,
            step_name=step.name,
            status="success",
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            output={"total_items_processed": len(items)}
        )
        context.step_results.append(result)
        self.logger.log_step_result(result)

    def _handle_if_step(self, step: Step, evaluated_params: Dict[str, Any], context: ExecutionContext, start_time: datetime) -> None:
        left = evaluated_params.get("left")
        operator = evaluated_params.get("operator", "equals")
        right = evaluated_params.get("right")

        if "condition" in evaluated_params and "left" not in evaluated_params:
            condition_met = self._evaluate_condition_expr(evaluated_params["condition"])
        else:
            condition_met = self._evaluate_condition(left, operator, right)

        sub_steps = step.sub_steps or []
        else_steps = step.else_steps or []
        executed_count = 0
        branch = "none"

        if condition_met:
            for sub_step in sub_steps:
                self._execute_step(sub_step, context)
            executed_count = len(sub_steps)
            branch = "then"
            status = "success"
        elif else_steps:
            for else_step in else_steps:
                self._execute_step(else_step, context)
            executed_count = len(else_steps)
            branch = "else"
            status = "success"
        else:
            status = "skipped"

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = StepResult(
            step_id=step.id,
            step_name=step.name,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            output={
                "condition_met": condition_met,
                "branch_executed": branch,
                "left": left,
                "operator": operator,
                "right": right,
                "executed_steps": executed_count
            }
        )
        context.step_results.append(result)
        self.logger.log_step_result(result)

    def _evaluate_condition(self, left: Any, operator: str, right: Any) -> bool:
        op = (operator or "equals").lower().strip()

        if op in ["is_empty", "empty"]:
            return left is None or str(left).strip() == ""
        if op in ["is_not_empty", "not_empty"]:
            return left is not None and str(left).strip() != ""

        if op in ["greater_than", ">", "gt"]:
            try:
                return float(left) > float(right)
            except (ValueError, TypeError):
                return False
        if op in ["greater_than_or_equal", ">=", "gte"]:
            try:
                return float(left) >= float(right)
            except (ValueError, TypeError):
                return False
        if op in ["less_than", "<", "lt"]:
            try:
                return float(left) < float(right)
            except (ValueError, TypeError):
                return False
        if op in ["less_than_or_equal", "<=", "lte"]:
            try:
                return float(left) <= float(right)
            except (ValueError, TypeError):
                return False

        s_left = "" if left is None else str(left).strip()
        s_right = "" if right is None else str(right).strip()

        if op in ["equals", "==", "eq"]:
            return s_left.lower() == s_right.lower()
        if op in ["not_equals", "!=", "neq"]:
            return s_left.lower() != s_right.lower()
        if op in ["contains", "in"]:
            return s_right.lower() in s_left.lower()
        if op in ["not_contains", "not_in"]:
            return s_right.lower() not in s_left.lower()
        if op in ["starts_with", "startswith"]:
            return s_left.lower().startswith(s_right.lower())
        if op in ["ends_with", "endswith"]:
            return s_left.lower().endswith(s_right.lower())

        return s_left == s_right

    def _evaluate_condition_expr(self, expr: Any) -> bool:
        if isinstance(expr, bool):
            return expr
        s = str(expr).strip()
        for token, mapped_op in [
            ("==", "equals"),
            ("!=", "not_equals"),
            (">=", "greater_than_or_equal"),
            ("<=", "less_than_or_equal"),
            (">", "greater_than"),
            ("<", "less_than"),
            (" contains ", "contains"),
            (" in ", "in"),
        ]:
            if token in s:
                parts = s.split(token, 1)
                left = parts[0].strip().strip("'\"")
                right = parts[1].strip().strip("'\"")
                return self._evaluate_condition(left, mapped_op, right)

        return s.lower() in ["true", "1", "yes"]
