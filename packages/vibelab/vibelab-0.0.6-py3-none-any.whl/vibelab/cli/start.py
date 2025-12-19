"""Start command."""

from __future__ import annotations

import collections
import logging
import os
import multiprocessing
import re
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import FrameType

import typer
import uvicorn

app = typer.Typer()

# Global reference to frontend process for cleanup
_frontend_process: subprocess.Popen[bytes] | None = None
_worker_processes: list[multiprocessing.Process] = []

_VITE_URL_RE = re.compile(r"http://(?:localhost|127\.0\.0\.1|\[::1\]):(?P<port>\d+)/?")


def _start_worker_process(worker_id: str) -> None:
    """Entry point for worker subprocesses.

    Must be a top-level function so it is pickleable under the `spawn`
    multiprocessing start method (macOS default).
    """
    from ..engine.worker import run_worker

    run_worker(worker_id=worker_id)


def _start_frontend_dev_server(
    *,
    web_dir: Path,
    frontend_host: str,
    preferred_port: int,
    api_url: str,
    project: str,
    verbose: bool,
) -> tuple[subprocess.Popen[bytes], str]:
    """Start Vite dev server and return (process, frontend_url).

    Even in non-verbose mode, we capture Vite output so that if it fails to start we can
    show the last lines of output rather than silently printing a dead URL.
    """
    env = os.environ.copy()
    env["PORT"] = str(preferred_port)
    env["VITE_API_URL"] = api_url
    env["VIBELAB_PROJECT"] = project

    # Let Vite auto-bump the port if needed; we'll parse the actual port from its output.
    cmd = [
        "bun",
        "run",
        "dev",
        "--",
        "--host",
        frontend_host,
        "--port",
        str(preferred_port),
    ]

    proc = subprocess.Popen(
        cmd,
        cwd=web_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )

    # Drain output in a background thread to avoid deadlocks if the buffer fills.
    buf: collections.deque[str] = collections.deque(maxlen=200)
    ready = threading.Event()
    discovered_url: list[str] = []

    def _reader() -> None:
        stdout = proc.stdout
        if stdout is None:
            return
        for raw in iter(stdout.readline, b""):
            line = raw.decode(errors="replace").rstrip("\n")
            buf.append(line)
            if verbose:
                sys.stderr.write(line + "\n")
                sys.stderr.flush()
            if not ready.is_set():
                m = _VITE_URL_RE.search(line)
                if m:
                    port = int(m.group("port"))
                    discovered_url.append(f"http://{frontend_host}:{port}/")
                    ready.set()

    threading.Thread(target=_reader, daemon=True).start()

    # Wait briefly for Vite to either print a URL or exit.
    deadline = time.time() + 6.0
    while time.time() < deadline:
        if ready.is_set() and discovered_url:
            return proc, discovered_url[0]
        if proc.poll() is not None:
            break
        time.sleep(0.05)

    if proc.poll() is not None:
        if not verbose:
            typer.echo("Frontend failed to start. Last output:", err=True)
            for line in list(buf)[-30:]:
                typer.echo(f"[vite] {line}", err=True)
        raise RuntimeError(f"frontend dev server exited (exit={proc.returncode})")

    # Still running but we didn't see a URL yet (unexpected). Assume preferred port.
    return proc, f"http://{frontend_host}:{preferred_port}/"


def _configure_logging(*, verbose: bool) -> None:
    """
    Configure user-friendly logging for `vibelab start`.

    - Normal mode: INFO-level, no per-request access logs from uvicorn.
    - Verbose mode: DEBUG-level, include access logs (uvicorn controls this).
    """
    level = logging.DEBUG if verbose else logging.INFO
    # Keep this minimal: uvicorn has its own log config; this mostly affects our own loggers.
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    os.environ["VIBELAB_LOG_LEVEL"] = "DEBUG" if verbose else "INFO"


def _cleanup_processes():
    """Clean up frontend + worker processes on exit."""
    global _frontend_process, _worker_processes

    for proc in _worker_processes:
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=5)
            if proc.is_alive():
                proc.kill()
    _worker_processes = []
    if _frontend_process:
        try:
            _frontend_process.terminate()
            _frontend_process.wait(timeout=5)
        except Exception:
            _frontend_process.kill()
        _frontend_process = None


@app.command()
def start_cmd(
    port: int = typer.Option(8000, "--port", help="Port to listen on"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
    frontend_port: int = typer.Option(5173, "--frontend-port", help="Frontend dev server port"),
    dev: bool = typer.Option(False, "--dev/--no-dev", help="Start in development mode (with frontend dev server)"),
    project: str = typer.Option("default", "--project", help="Project name (separate DB and files under VIBELAB_HOME/projects/<project>/)"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose logging (API access logs + frontend logs)"),
    workers: int = typer.Option(1, "--workers", help="Number of worker processes"),
) -> None:
    """Start the web server and frontend."""
    _configure_logging(verbose=verbose)

    # Display alpha warning
    typer.echo("", err=True)
    typer.echo("⚠️  ALPHA RELEASE - USE WITH CAUTION", err=True)
    typer.echo("This project is in alpha and under active development.", err=True)
    typer.echo("Breaking changes are expected and will occur. Use at your own risk.", err=True)
    typer.echo("", err=True)
    
    # Must be set before importing the FastAPI app module (uvicorn will import it).
    os.environ["VIBELAB_PROJECT"] = project

    from ..db.connection import get_project_home, init_db

    # Validate early so we can show a friendly CLI error.
    try:
        get_project_home(project)
    except Exception as e:
        raise typer.BadParameter(str(e), param_hint="--project") from e

    init_db()

    # Start worker(s) (durable queue consumers)
    global _worker_processes
    _worker_processes = []
    for i in range(max(1, workers)):
        worker_id = f"worker-{i+1}"
        proc = multiprocessing.Process(target=_start_worker_process, args=(worker_id,), name=worker_id)
        proc.start()
        _worker_processes.append(proc)

    # Frontend paths:
    # - Production/static: prefer the installed package path (`vibelab/web/dist`) if present.
    # - Dev (Vite): must use a directory that contains `package.json` (source checkout `./web`).
    package_dir = Path(__file__).parent.parent  # .../src/vibelab
    repo_root = Path(__file__).resolve().parents[3]

    package_web_dir = package_dir / "web"
    package_dist_dir = package_web_dir / "dist"
    source_web_dir = repo_root / "web"
    source_dist_dir = source_web_dir / "dist"

    # Default to package dist if present, else source dist.
    web_dir = package_web_dir if package_dist_dir.exists() else source_web_dir
    dist_dir = package_dist_dir if package_dist_dir.exists() else source_dist_dir

    if dev:
        # Dev mode requires the source `web/` directory (or any directory with a package.json).
        dev_web_dir = source_web_dir if (source_web_dir / "package.json").exists() else package_web_dir
        if not (dev_web_dir / "package.json").exists():
            typer.echo(
                "Failed to start frontend in --dev mode: could not find `package.json` for the Vite app.",
                err=True,
            )
            typer.echo(f"Looked in: {source_web_dir}", err=True)
            typer.echo(f"Looked in: {package_web_dir}", err=True)
            typer.echo("Tip: run from a source checkout, or start without --dev to use the built frontend.", err=True)
            raise typer.Exit(code=1)

        # Development mode: start both backend and frontend dev servers
        typer.echo("Starting VibeLab in development mode...", err=True)
        # Use 127.0.0.1 explicitly to avoid any localhost IPv6/IPv4 surprises.
        frontend_host = "127.0.0.1"
        # We'll print the final URL after Vite starts (it may auto-bump the port).
        typer.echo(f"API:      http://{host}:{port}", err=True)
        typer.echo(f"Worker:   {workers} process(es)", err=True)
        if not verbose:
            typer.echo("Tip: run with --verbose to see frontend logs and API access logs.", err=True)

        # Set up signal handlers for cleanup
        def signal_handler(sig: int, frame: FrameType | None) -> None:
            typer.echo("\nShutting down...", err=True)
            _cleanup_processes()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start frontend dev server
        global _frontend_process
        try:
            _frontend_process, frontend_url = _start_frontend_dev_server(
                web_dir=dev_web_dir,
                frontend_host=frontend_host,
                preferred_port=frontend_port,
                api_url=f"http://{host}:{port}",
                project=project,
                verbose=verbose,
            )
            typer.echo(f"Frontend: {frontend_url}", err=True)
        except Exception as e:
            typer.echo(f"Failed to start frontend: {e}", err=True)
            typer.echo("Continuing with backend only...", err=True)

        # Start backend server
        try:
            uvicorn.run(
                "vibelab.api.app:app",
                host=host,
                port=port,
                reload=False,  # Don't use uvicorn reload when managing frontend separately
                log_level="debug" if verbose else "info",
                access_log=verbose,
            )
        except (KeyboardInterrupt, SystemExit):
            signal_handler(signal.SIGINT, None)
        finally:
            _cleanup_processes()
    else:
        # Production mode: serve static files from backend
        if not dist_dir.exists():
            typer.echo(
                "Warning: Frontend not built. Run 'cd web && bun run build' first.",
                err=True,
            )
            typer.echo("Starting backend only...", err=True)

        typer.echo("Starting VibeLab...", err=True)
        typer.echo(f"Frontend: http://{host}:{port}", err=True)
        typer.echo(f"API:      http://{host}:{port}/api", err=True)
        typer.echo(f"Worker:   {workers} process(es)", err=True)
        if not verbose:
            typer.echo("Tip: run with --verbose to see API access logs.", err=True)

        uvicorn.run(
            "vibelab.api.app:app",
            host=host,
            port=port,
            reload=False,
            log_level="debug" if verbose else "info",
            access_log=verbose,
        )
