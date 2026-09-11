from datetime import datetime
from typing import Any, Dict, Optional

from .evaluator import VariableEvaluator
from .logger import ExecutionLogger
from ..actions.registry import ActionRegistry
from ..models.context import ExecutionContext, StepResult
from ..models.flow import FlowDefinition, Step


class FlowInterpreter:
    """
    Interpreter that parses FlowDefinition, evaluates expressions, and executes steps sequentially.
    """

    def __init__(self, logger: Optional[ExecutionLogger] = None):
        self.logger = logger or ExecutionLogger()

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

        if step.action == "logic.loop":
            self._handle_loop_step(step, evaluated_params, context, start_time)
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
            error_type = "Business" if "Business" in type(e).__name__ else "Technical"

            result = StepResult(
                step_id=step.id,
                step_name=step.name,
                status="failed",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                error_message=str(e),
                error_type=error_type
            )
            context.step_results.append(result)
            self.logger.log_step_result(result)

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
