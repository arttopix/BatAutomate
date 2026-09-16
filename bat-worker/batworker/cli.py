import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .runner import WorkerRunner


def main():
    parser = argparse.ArgumentParser(
        prog="batworker",
        description="BAT Worker: Unattended Robot Daemon and Edge Execution Engine"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"batworker {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: info
    subparsers.add_parser("info", help="Display worker machine hardware, architecture, and runtime stats")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Execute a flow or project bundle on this worker")
    run_parser.add_argument("flow_path", help="Path to flow.json or project bundle directory")
    run_parser.add_argument("--sandbox", action="store_true", help="Execute inside an isolated temporary sandbox workspace")
    run_parser.add_argument("--vars", type=str, help="JSON string of variables to inject (e.g. '{\"env\":\"prod\"}')")
    run_parser.add_argument("--log-dir", type=str, help="Custom directory path to store execution logs")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    runner = WorkerRunner()

    if args.command == "info":
        info = runner.get_system_info()
        print("BAT Worker System Information:")
        print("-------------------------------")
        for k, v in info.items():
            print(f"  {k}: {v}")
        sys.exit(0)

    if args.command == "run":
        extra_vars = {}
        if args.vars:
            try:
                extra_vars = json.loads(args.vars)
            except Exception as e:
                print(f"Error parsing --vars JSON: {e}", file=sys.stderr)
                sys.exit(1)

        try:
            res = runner.execute_flow(
                flow_path_or_alias=args.flow_path,
                extra_vars=extra_vars,
                use_sandbox=args.sandbox,
                log_dir=args.log_dir
            )

            print("Execution Result:")
            print(f"  Job ID: {res['job_id']}")
            print(f"  Flow Name: {res['flow_name']}")
            print(f"  Status: {res['status'].upper()}")
            print(f"  Duration: {res['duration_seconds']}s")
            print(f"  Steps Executed: {res['steps_executed']}/{res['steps_total']}")
            if res["has_error"]:
                print(f"  Error Details: {res['error']}")
                sys.exit(1)
            else:
                sys.exit(0)

        except Exception as e:
            print(f"Worker execution failed with error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
