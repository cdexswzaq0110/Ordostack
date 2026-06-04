from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.error import URLError
from urllib.request import urlopen


DASHBOARD_URL = os.getenv("ORDOSTACK_DASHBOARD_URL", "http://localhost:5173")
OUTPUT_DIR = Path(os.getenv("ORDOSTACK_BROWSER_SMOKE_DIR", "artifacts/browser-smoke"))
SCREENSHOT_MIN_BYTES = 8_000


def fetch_text(url: str) -> str:
    with urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8")


def browser_candidates() -> list[Path]:
    path_candidates = [
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    windows_candidates = [
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LocalAppData", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe",
    ]
    return [Path(candidate) for candidate in path_candidates if candidate] + windows_candidates


def find_browser() -> Path:
    for candidate in browser_candidates():
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Chrome or Edge executable not found")


def capture_screenshot(browser_path: Path, screenshot_path: Path) -> None:
    screenshot_path = screenshot_path.resolve()
    profile_dir = (OUTPUT_DIR / "profile").resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    for headless_flag in ("--headless=new", "--headless"):
        command = [
            str(browser_path),
            headless_flag,
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-first-run",
            "--disable-extensions",
            "--window-size=1440,1000",
            f"--user-data-dir={profile_dir}",
            f"--screenshot={screenshot_path}",
            DASHBOARD_URL,
        ]
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=45)
        if completed.returncode == 0:
            return

        errors.append(
            f"{headless_flag}: {(completed.stderr.strip() or completed.stdout.strip() or 'browser screenshot failed')}",
        )

    raise RuntimeError("; ".join(errors))


def assert_png_screenshot(path: Path) -> int:
    if not path.exists():
        raise AssertionError(f"screenshot was not created: {path}")

    size = path.stat().st_size
    if size < SCREENSHOT_MIN_BYTES:
        raise AssertionError(f"screenshot is too small: {size} bytes")

    with path.open("rb") as file:
        signature = file.read(8)
    if signature != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("screenshot is not a PNG file")

    return size


def main() -> int:
    try:
        dashboard_html = fetch_text(DASHBOARD_URL)
        if "OrdoStack" not in dashboard_html:
            raise AssertionError("dashboard HTML does not contain OrdoStack")

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        browser_path = find_browser()
        screenshot_path = OUTPUT_DIR / "dashboard.png"
        capture_screenshot(browser_path=browser_path, screenshot_path=screenshot_path)
        screenshot_bytes = assert_png_screenshot(screenshot_path)

        result = {
            "status": "ok",
            "checked_at": datetime.now().isoformat(timespec="seconds"),
            "dashboard_url": DASHBOARD_URL,
            "browser": str(browser_path),
            "screenshot_path": str(screenshot_path),
            "screenshot_bytes": screenshot_bytes,
        }
        metadata_path = OUTPUT_DIR / "browser-smoke.json"
        metadata_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0
    except (AssertionError, FileNotFoundError, RuntimeError, TimeoutError, URLError) as error:
        print(f"Browser smoke failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
