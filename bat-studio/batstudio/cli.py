import argparse
import sys
import threading
import time
import webbrowser
import uvicorn

from . import __version__


def _launch_browser(url: str):
    # Wait briefly for uvicorn server to bind and start accepting connections
    time.sleep(0.8)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(
        prog="batstudio",
        description="BAT Studio: Developer Studio, Step Inspector, and Live Debugger for BAT Automate"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"batstudio {__version__}"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes (development mode)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not automatically launch the web browser"
    )

    args = parser.parse_args()

    server_url = f"http://{args.host}:{args.port}/docs"

    print("==================================================")
    print(f"BAT Studio Server v{__version__}")
    print(f"Listening on: http://{args.host}:{args.port}")
    print(f"Swagger API Docs: {server_url}")
    if not args.no_browser:
        print("Launching web browser automatically...")
    print("==================================================")

    if not args.no_browser:
        threading.Thread(target=_launch_browser, args=(server_url,), daemon=True).start()

    uvicorn.run(
        "batstudio.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
