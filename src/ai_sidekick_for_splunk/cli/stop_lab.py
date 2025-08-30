"""Stop the AI Sidekick lab environment with OS-aware launcher.

This CLI resolves the project root, detects the operating system, and executes
the appropriate stop script:

- Unix/macOS: scripts/lab/stop-lab-setup.sh
- Windows: scripts/lab/stop-lab-setup.ps1

Usage (via project script):
    uv run stop-lab
"""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """Locate the project root by searching upward for pyproject.toml.

    Args:
        start: Optional starting path. Defaults to this file's directory.

    Returns:
        Path to the project root directory.

    Raises:
        FileNotFoundError: If no pyproject.toml is found up the tree.
    """
    current_path: Path = (start or Path(__file__).resolve()).parent
    for parent in [current_path, *current_path.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("Could not locate project root (pyproject.toml not found)")


def run_command(command: list[str], cwd: Path) -> int:
    """Run a subprocess command in the given working directory.

    Args:
        command: Command and arguments to execute.
        cwd: Working directory for the subprocess.

    Returns:
        Process return code.
    """
    try:
        completed = subprocess.run(command, cwd=str(cwd))
        return int(completed.returncode)
    except FileNotFoundError as exc:
        print(f"[ERROR] Command not found: {command[0]} ({exc})", file=sys.stderr)
        return 127
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] Failed to execute command: {' '.join(command)}\n{exc}", file=sys.stderr)
        return 1


def main() -> None:
    """Entry point that dispatches to the OS-specific stop script."""
    project_root = find_project_root()
    system_name = platform.system().lower()

    if system_name.startswith("win"):
        script_path = project_root / "scripts" / "lab" / "stop-lab-setup.ps1"
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
        ]
    else:
        script_path = project_root / "scripts" / "lab" / "stop-lab-setup.sh"
        command = ["bash", str(script_path)]

    if not script_path.exists():
        print(f"[ERROR] Stop script not found: {script_path}", file=sys.stderr)
        sys.exit(1)

    exit_code = run_command(command, cwd=project_root)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
