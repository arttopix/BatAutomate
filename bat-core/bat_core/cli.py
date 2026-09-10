import argparse
import json
import sys
from pathlib import Path

from .models.flow import FlowDefinition
from .engine.interpreter import FlowInterpreter
from .engine.logger import ExecutionLogger


def main():
    parser = argparse.ArgumentParser(description="bat-core CLI Runner")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    run_parser = subparsers.add_parser("run", help="Run a Flow JSON file")
    run_parser.add_argument("flow_file", help="Path to flow.json file")
    run_parser.add_argument("--vars", help="Optional JSON string of variables to override", default=None)
    run_parser.add_argument("--log-dir", help="Directory to save execution JSON logs", default=None)

    args = parser.parse_args()

    if args.command == "run":
        flow_path = Path(args.flow_file)
        if not flow_path.exists():
            print(f"Error: Flow file '{args.flow_file}' does not exist.", file=sys.stderr)
            sys.exit(1)

        try:
            content = flow_path.read_text(encoding="utf-8")
            raw_json = json.loads(content)
            flow_def = FlowDefinition.model_validate(raw_json)
        except Exception as e:
            print(f"Error parsing flow JSON: {str(e)}", file=sys.stderr)
            sys.exit(1)

        extra_vars = {}
        if args.vars:
            try:
                extra_vars = json.loads(args.vars)
            except Exception as e:
                print(f"Error parsing --vars JSON: {str(e)}", file=sys.stderr)
                sys.exit(1)

        logger = ExecutionLogger(log_dir=args.log_dir)
        interpreter = FlowInterpreter(logger=logger)
        context = interpreter.run_flow(flow_def, initial_vars=extra_vars)

        if context.has_error:
            sys.exit(1)
        sys.exit(0)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
