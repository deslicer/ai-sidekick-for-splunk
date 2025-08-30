"""Integrate an agent with the orchestrator (OS-aware launcher).

Dispatches to the platform-specific integrate script and passes through
any additional command-line arguments (e.g., agent name).

- Unix/macOS: scripts/agent/integrate-agent.sh
- Windows: scripts/agent/integrate-agent.ps1

Usage (via project script):
    uv run integrate-agent <agent_name>
"""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """Locate the project root by searching upward for pyproject.toml."""
    current_path: Path = (start or Path(__file__).resolve()).parent
    for parent in [current_path, *current_path.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("Could not locate project root (pyproject.toml not found)")


def run_command(command: list[str], cwd: Path) -> int:
    """Run a subprocess command in the given working directory."""
    try:
        completed = subprocess.run(command, cwd=str(cwd))
        return int(completed.returncode)
    except FileNotFoundError as exc:
        print(f"[ERROR] Command not found: {command[0]} ({exc})", file=sys.stderr)
        return 127
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] Failed to execute command: {' '.join(command)}\n{exc}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> None:
    """Entry point that dispatches to the OS-specific integrate script.

    Args:
        argv: Optional argument list (excluding program name). Uses sys.argv[1:] if None.
    """
    args = list(argv) if argv is not None else sys.argv[1:]
    project_root = find_project_root()
    system_name = platform.system().lower()

    if system_name.startswith("win"):
        script_path = project_root / "scripts" / "agent" / "integrate-agent.ps1"
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            *args,
        ]
    else:
        script_path = project_root / "scripts" / "agent" / "integrate-agent.sh"
        command = ["bash", str(script_path), *args]

    if not script_path.exists():
        print(f"[ERROR] Integrate script not found: {script_path}", file=sys.stderr)
        sys.exit(1)

    exit_code = run_command(command, cwd=project_root)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
