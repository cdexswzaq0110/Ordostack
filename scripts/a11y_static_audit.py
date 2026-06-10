from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path.cwd()
    app_path = root / "web-dashboard" / "src" / "App.tsx"
    styles_path = root / "web-dashboard" / "src" / "styles.css"
    app_text = app_path.read_text(encoding="utf-8")
    styles_text = styles_path.read_text(encoding="utf-8")

    checks = {
        "buttons_have_aria_usage": "aria-label" in app_text,
        "language_switcher_is_labeled": 'aria-label={t("Language")}' in app_text,
        "select_focus_visible": "select:focus-visible" in styles_text,
        "keyboard_focus_visible": ":focus-visible" in styles_text,
        "timeline_actions_are_labeled": "Move earlier" in app_text and "Move later" in app_text,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        print("A11y static audit failed:")
        for name in failed:
            print(f"  {name}")
        return 1

    print("A11y static audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
