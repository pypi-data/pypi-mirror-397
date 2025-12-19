"""Database connection and initialization."""

import os
import re
import shutil
import sqlite3
from collections.abc import Generator
from pathlib import Path

from .migrations import migrate

_DEFAULT_PROJECT = "default"


def get_vibelab_home() -> Path:
    """
    Get VibeLab *root* data directory.

    This is configurable via `VIBELAB_HOME` and contains a `projects/` subdir.
    """
    home = os.environ.get("VIBELAB_HOME")
    if home:
        return Path(home).expanduser()
    return Path.home() / ".vibelab"


def get_vibelab_project() -> str:
    """Get the active project name (defaults to 'default')."""
    return os.environ.get("VIBELAB_PROJECT", _DEFAULT_PROJECT)


def _validate_project_name(name: str) -> str:
    """
    Validate project name for filesystem safety.

    Allowed: letters, numbers, underscore, dash (1..64 chars).
    """
    name = name.strip()
    if not name:
        raise ValueError("Project name cannot be empty")
    if len(name) > 64:
        raise ValueError("Project name too long (max 64 chars)")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValueError("Invalid project name (use only letters, numbers, '_' and '-')")
    return name


def get_projects_dir() -> Path:
    """Get (and ensure) the `projects/` directory inside `VIBELAB_HOME`."""
    root = get_vibelab_home()
    root.mkdir(parents=True, exist_ok=True)
    projects_dir = root / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    return projects_dir


def get_project_home(project: str | None = None) -> Path:
    """Get (and ensure) the active project's directory under `projects/<project>/`."""
    name = _validate_project_name(project or get_vibelab_project())
    project_dir = get_projects_dir() / name
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def get_results_dir(project: str | None = None) -> Path:
    """Get (and ensure) the active project's results directory."""
    results_dir = get_project_home(project) / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def get_worktrees_dir(project: str | None = None) -> Path:
    """Get (and ensure) the active project's worktrees directory."""
    worktrees_dir = get_project_home(project) / "worktrees"
    worktrees_dir.mkdir(parents=True, exist_ok=True)
    return worktrees_dir


def get_containers_dir(project: str | None = None) -> Path:
    """Get (and ensure) the active project's containers directory."""
    containers_dir = get_project_home(project) / "containers"
    containers_dir.mkdir(parents=True, exist_ok=True)
    return containers_dir


def get_modal_dir(project: str | None = None) -> Path:
    """Get (and ensure) the active project's Modal temp directory."""
    modal_dir = get_project_home(project) / "modal"
    modal_dir.mkdir(parents=True, exist_ok=True)
    return modal_dir


def get_repos_dir() -> Path:
    """Get (and ensure) the shared repos directory for bare clones.

    This is a global directory (not per-project) since repos are shared across projects.
    Structure: ~/.vibelab/repos/{host}/{owner}/{repo}
    """
    repos_dir = get_vibelab_home() / "repos"
    repos_dir.mkdir(parents=True, exist_ok=True)
    return repos_dir


def _maybe_migrate_legacy_root_layout(project: str) -> None:
    """
    One-time migration: move legacy root-level `data.db`/`results/`/... into
    `projects/default/` when the active project is default.
    """
    if project != _DEFAULT_PROJECT:
        return

    root = get_vibelab_home()
    legacy_db = root / "data.db"
    legacy_results = root / "results"
    legacy_worktrees = root / "worktrees"
    legacy_containers = root / "containers"
    legacy_modal = root / "modal"

    proj = get_project_home(project)

    def move_if_present(src: Path, dst: Path) -> None:
        if not src.exists():
            return
        if dst.exists():
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

    move_if_present(legacy_db, proj / "data.db")
    move_if_present(legacy_results, proj / "results")
    move_if_present(legacy_worktrees, proj / "worktrees")
    move_if_present(legacy_containers, proj / "containers")
    move_if_present(legacy_modal, proj / "modal")


def get_db_path() -> Path:
    """Get database file path."""
    project = _validate_project_name(get_vibelab_project())
    _maybe_migrate_legacy_root_layout(project)
    return get_project_home(project) / "data.db"


def _configure_sqlite_connection(conn: sqlite3.Connection) -> None:
    """
    Apply SQLite connection pragmas.

    Notes:
    - WAL mode improves concurrency for API + worker.
    - busy_timeout helps avoid transient "database is locked" errors.
    - foreign_keys must be enabled per-connection in SQLite.
    """
    # Enforce foreign key constraints declared in schema.
    conn.execute("PRAGMA foreign_keys = ON")

    # Better concurrency for concurrent readers/writers.
    try:
        conn.execute("PRAGMA journal_mode = WAL")
    except sqlite3.OperationalError:
        # Some SQLite configurations might not allow WAL; proceed best-effort.
        pass

    busy_timeout_ms = int(os.environ.get("VIBELAB_SQLITE_BUSY_TIMEOUT_MS", "5000"))
    conn.execute(f"PRAGMA busy_timeout = {busy_timeout_ms}")


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Get database connection."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    _configure_sqlite_connection(conn)
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database with schema and migrations."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    _configure_sqlite_connection(conn)
    try:
        migrate(conn)
        conn.commit()
    finally:
        conn.close()
