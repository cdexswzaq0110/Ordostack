"""One-click OrdoStack launcher.

Starts Docker Desktop if needed, brings the Compose stack up, waits for every
service to report healthy, then opens the dashboard in the default browser.
Built into a standalone Windows executable with PyInstaller:

    # Windows PowerShell (repo root)
    python -m pip install pyinstaller
    pyinstaller --onefile --name OrdoStack --distpath dist scripts\\ordostack_launcher.py

The resulting dist\\OrdoStack.exe must be run from inside the repository (it
finds docker-compose.yml by walking up from its own location, falling back to
the current working directory).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

DASHBOARD_URL = "http://localhost:5173"
HEALTH_CHECKS = [
    ("backend-api", "http://localhost:8000/health"),
    ("scheduler-service", "http://localhost:8100/health"),
    ("ml-service", "http://localhost:8200/health"),
    ("web-dashboard", "http://localhost:5173"),
]
DOCKER_DESKTOP_PATHS = [
    Path(r"C:\Program Files\Docker\Docker\Docker Desktop.exe"),
    Path(r"C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"),
]
DAEMON_WAIT_SECONDS = 300
HEALTH_WAIT_SECONDS = 600


def find_project_root() -> Path:
    """Walk up from the executable (or script) looking for docker-compose.yml."""
    anchor = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve()
    for candidate in [anchor.parent, *anchor.parents]:
        if (candidate / "docker-compose.yml").exists():
            return candidate
    cwd = Path.cwd()
    if (cwd / "docker-compose.yml").exists():
        return cwd
    raise SystemExit(
        "docker-compose.yml not found. Place OrdoStack.exe inside the OrdoStack "
        "repository (e.g. the repo root or dist/) and run it again."
    )


def docker_daemon_ready() -> bool:
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, timeout=20, creationflags=subprocess.CREATE_NO_WINDOW
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def ensure_docker_running() -> None:
    try:
        subprocess.run(["docker", "--version"], capture_output=True, timeout=20, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        raise SystemExit("Docker CLI not found. Install Docker Desktop first: https://docs.docker.com/desktop/")

    if docker_daemon_ready():
        print("[1/4] Docker daemon already running.")
        return

    desktop = next((path for path in DOCKER_DESKTOP_PATHS if path.exists()), None)
    if desktop is None:
        raise SystemExit("Docker daemon is not running and Docker Desktop was not found. Start Docker manually.")

    print("[1/4] Starting Docker Desktop...")
    os.startfile(str(desktop))  # noqa: S606 - launching a known local application
    deadline = time.time() + DAEMON_WAIT_SECONDS
    while time.time() < deadline:
        if docker_daemon_ready():
            print("      Docker daemon is ready.")
            return
        time.sleep(5)
    raise SystemExit(f"Docker daemon did not become ready within {DAEMON_WAIT_SECONDS} seconds.")


def compose_up(project_root: Path) -> None:
    print("[2/4] Starting the OrdoStack stack (docker compose up -d)...")
    result = subprocess.run(
        ["docker", "compose", "up", "-d"],
        cwd=project_root,
        creationflags=subprocess.CREATE_NO_WINDOW,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit("docker compose up failed; see output above.")


def url_responds(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return 200 <= response.status < 500
    except OSError:
        return False


def wait_for_health() -> None:
    print("[3/4] Waiting for services to become healthy...")
    pending = dict(HEALTH_CHECKS)
    deadline = time.time() + HEALTH_WAIT_SECONDS
    while pending and time.time() < deadline:
        for name, url in list(pending.items()):
            if url_responds(url):
                print(f"      {name} is up.")
                del pending[name]
        if pending:
            time.sleep(3)
    if pending:
        raise SystemExit(
            "These services did not come up in time: "
            + ", ".join(pending)
            + ". Check `docker compose ps` and `docker compose logs`."
        )


def main() -> int:
    print("OrdoStack launcher")
    print("==================")
    project_root = find_project_root()
    print(f"Project root: {project_root}")
    ensure_docker_running()
    compose_up(project_root)
    wait_for_health()
    print(f"[4/4] Opening {DASHBOARD_URL} ...")
    webbrowser.open(DASHBOARD_URL)
    print("Done. The stack keeps running in the background; stop it with `docker compose down`.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as exit_info:
        if exit_info.code not in (0, None):
            print(f"\nERROR: {exit_info.code}" if isinstance(exit_info.code, str) else "")
            input("Press Enter to close...")
        raise
