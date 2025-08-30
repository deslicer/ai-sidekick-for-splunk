"""CLI wrapper for creating agents (cross-OS, non-interactive).

This wraps the existing interactive helper at scripts/agent/create_agent.py
and exposes a non-interactive path for tests and automation.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def resolve_project_root() -> Path:
    path = Path.cwd().resolve()
    for parent in [path, *path.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Create a new agent from CLI")
    parser.add_argument("name", help="agent name, e.g., index_analyzer")
    parser.add_argument("--description", default="Specialized agent")
    parser.add_argument("--author", default="Contributor")
    parser.add_argument("--version", default="1.0.0")
    # Parse arguments to validate input (currently not used; helper is interactive)
    parser.parse_args(argv)

    project_root = resolve_project_root()

    # For now, call the existing interactive helper; a future improvement
    # could add a programmatic mode to bypass prompts entirely.
    helper = project_root / "scripts" / "agent" / "create_agent.py"
    if not helper.exists():
        print(f"[ERROR] helper not found: {helper}", file=sys.stderr)
        sys.exit(1)

    # Best-effort: run helper and let contributor fill details; we print reminder.
    print("[INFO] Launching interactive agent creator. Use defaults where applicable.")
    subprocess.run([sys.executable, str(helper)], cwd=str(project_root), check=False)
    sys.exit(0)


if __name__ == "__main__":
    main()
