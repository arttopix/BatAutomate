import argparse
import json
import platform
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import __version__
from .models.flow import FlowDefinition
from .engine.interpreter import FlowInterpreter
from .engine.logger import ExecutionLogger


def _get_project_root() -> Optional[Path]:
    curr = Path.cwd().resolve()
    for p in [curr] + list(curr.parents):
        if (p / ".git").exists() or (p / "bat-core").is_dir():
            return p
    return None


def _get_search_directories() -> List[Path]:
    dirs = [
        Path.cwd(),
        Path.cwd() / "flows",
        Path.cwd() / "examples",
        Path(__file__).parent.parent / "examples",
        Path.home() / ".batautomate" / "flows",
    ]
    root = _get_project_root()
    if root:
        dirs.insert(1, root / "flows")
        dirs.append(root / "examples")

    unique_dirs = []
    seen = set()
    for d in dirs:
        if d.exists() and d.resolve() not in seen:
            seen.add(d.resolve())
            unique_dirs.append(d.resolve())
    return unique_dirs


def discover_flows() -> Dict[str, Tuple[Path, str]]:
    """
    Discovers available flow JSON files and Self-Contained Project Bundles across search directories.
    Returns dict mapping flow alias/name to (file_path, description).
    """
    discovered: Dict[str, Tuple[Path, str]] = {}

    for search_dir in _get_search_directories():
        # 1. Discover Self-Contained Project Bundles (directories with flow.json)
        for flow_file in search_dir.glob("**/flow.json"):
            parts = flow_file.parts
            if any(p.startswith(".") or p in ["__pycache__", "subflows", "node_modules", ".venv", "venv"] for p in parts):
                continue
            try:
                data = json.loads(flow_file.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "steps" in data:
                    name = data.get("name", flow_file.parent.name)
                    alias = flow_file.parent.name
                    discovered[alias] = (flow_file, name)
                    # Also register namespaced alias relative to search_dir (e.g. benchmarks/rpachallenge)
                    try:
                        rel = flow_file.parent.relative_to(search_dir)
                        rel_str = str(rel).replace("\\", "/")
                        if rel_str and rel_str != alias:
                            discovered[rel_str] = (flow_file, name)
                    except ValueError:
                        pass
            except Exception:
                continue

        # 2. Discover flat flow files (*.json)
        for json_file in search_dir.glob("*.json"):
            if json_file.name == "flow.json":
                continue
            if json_file.name.endswith("_flow.json") or json_file.parent.name in ["examples", "flows"]:
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    if isinstance(data, dict) and "steps" in data:
                        name = data.get("name", json_file.stem)
                        alias = json_file.stem
                        if alias.endswith("_flow"):
                            alias = alias[:-5]
                        if alias not in discovered:
                            discovered[alias] = (json_file, name)
                except Exception:
                    continue
    return discovered


def resolve_flow_path(flow_input: str) -> Optional[Path]:
    """
    Smart Flow Resolver: resolves a flow name, alias, project directory, or path into an absolute file path.
    """
    # 1. Exact path or relative path to file
    direct_path = Path(flow_input)
    if direct_path.is_file():
        return direct_path.resolve()

    # 2. Direct path to a project directory containing flow.json
    if direct_path.is_dir() and (direct_path / "flow.json").is_file():
        return (direct_path / "flow.json").resolve()

    # 3. Direct path with .json
    json_path = Path(f"{flow_input}.json")
    if json_path.is_file():
        return json_path.resolve()

    # 4. Search in discovered flows (aliases & project bundles)
    flows = discover_flows()
    if flow_input in flows:
        return flows[flow_input][0].resolve()

    if f"{flow_input}_flow" in flows:
        return flows[f"{flow_input}_flow"][0].resolve()

    # 5. Search directories for project bundles or files
    for search_dir in _get_search_directories():
        candidates = [
            search_dir / flow_input / "flow.json",
            search_dir / flow_input,
            search_dir / f"{flow_input}.json",
            search_dir / f"{flow_input}_flow.json",
        ]
        for c in candidates:
            if c.is_file():
                return c.resolve()
            if c.is_dir() and (c / "flow.json").is_file():
                return (c / "flow.json").resolve()

        # Check recursive directory match (e.g. flows/**/<flow_input>/flow.json)
        for matched in search_dir.glob(f"**/{flow_input}/flow.json"):
            if matched.is_file():
                return matched.resolve()

    return None


def main():
    parser = argparse.ArgumentParser(prog="batautomate", description="BAT Automate - Enterprise RPA CLI Runner")
    parser.add_argument("-v", "--version", action="version", version=f"batautomate {__version__}")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Run an RPA Flow by name or path (e.g. 'batautomate run rpachallenge')")
    run_parser.add_argument("flow_file", help="Flow name or path to flow.json file")
    run_parser.add_argument("--vars", help="Optional JSON string of variables to override", default=None)
    run_parser.add_argument("--log-dir", help="Directory to save execution JSON logs (default: auto-detected project root 'logs/')", default=None)

    # Command: list
    subparsers.add_parser("list", help="List all discovered RPA Flows available to run")

    # Command: version
    subparsers.add_parser("version", help="Show BAT Automate version and environment details")

    # Command: install-browsers
    subparsers.add_parser("install-browsers", help="Download and install Playwright Chromium browser")

    args = parser.parse_args()

    if args.command == "version":
        print(f"BAT Automate: v{__version__}")
        print(f"Python:       {platform.python_version()} ({platform.python_implementation()})")
        print(f"Platform:     {platform.system()} {platform.release()} ({platform.machine()})")
        sys.exit(0)

    elif args.command == "install-browsers":
        import subprocess
        print("Installing Playwright Chromium browser for BAT Automate...")
        res = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
        if res.returncode == 0:
            print("Chromium browser successfully installed.")
        else:
            print("Installation failed. On Linux/Raspberry Pi, you may also need: sudo playwright install-deps chromium", file=sys.stderr)
        sys.exit(res.returncode)

    elif args.command == "list":
        flows = discover_flows()
        if not flows:
            print("No flows found in current directory, 'flows/', 'examples/', or ~/.batautomate/flows/.")
            print("Tip: You can specify full file path with: batautomate run <path_to_flow.json>")
            sys.exit(0)

        print("\nAvailable Flows in BAT Automate:")
        print("-" * 65)
        for alias, (path, name) in sorted(flows.items()):
            print(f"  {alias:<18} | {name:<25} | {path}")
        print("-" * 65)
        print("To run a flow: batautomate run <flow_name>\n")
        sys.exit(0)

    elif args.command == "run":
        resolved_path = resolve_flow_path(args.flow_file)
        if not resolved_path:
            print(f"Error: Could not find flow '{args.flow_file}'.", file=sys.stderr)
            flows = discover_flows()
            if flows:
                print("\nAvailable flows you can run:", file=sys.stderr)
                for alias, (_, name) in sorted(flows.items()):
                    print(f"  - {alias:<16} ({name})", file=sys.stderr)
            print("\nTip: You can also specify full file path: batautomate run <path_to_flow.json>", file=sys.stderr)
            sys.exit(1)

        try:
            content = resolved_path.read_text(encoding="utf-8")
            raw_json = json.loads(content)
            flow_def = FlowDefinition.model_validate(raw_json)
        except Exception as e:
            print(f"Error parsing flow JSON at '{resolved_path}': {str(e)}", file=sys.stderr)
            sys.exit(1)

        extra_vars = {}
        if args.vars:
            try:
                extra_vars = json.loads(args.vars)
            except Exception as e:
                print(f"Error parsing --vars JSON: {str(e)}", file=sys.stderr)
                sys.exit(1)

        extra_vars["__flow_dir__"] = str(resolved_path.parent)

        logger = ExecutionLogger(log_dir=args.log_dir, flow_path=resolved_path)
        interpreter = FlowInterpreter(logger=logger)
        context = interpreter.run_flow(flow_def, initial_vars=extra_vars)

        if context.has_error:
            sys.exit(1)
        sys.exit(0)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
