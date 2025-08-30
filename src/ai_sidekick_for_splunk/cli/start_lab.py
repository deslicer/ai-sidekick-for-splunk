"""Start the AI Sidekick lab environment with OS-aware launcher.

This CLI resolves the project root, detects the operating system, and executes
the appropriate startup script:

- Unix/macOS: scripts/lab/start-lab-setup.sh
- Windows: scripts/lab/start-lab-setup.ps1

Usage (via project script):
    uv run start-lab
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

import httpx


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
        completed = subprocess.run(command, cwd=str(cwd), check=False)
        return int(completed.returncode)
    except FileNotFoundError as exc:
        print(f"[ERROR] Command not found: {command[0]} ({exc})", file=sys.stderr)
        return 127
    except OSError as exc:  # surface unexpected OS-level errors
        print(f"[ERROR] Failed to execute command: {' '.join(command)}\n{exc}", file=sys.stderr)
        return 1


def is_port_available(port: int) -> bool:
    """Check whether a TCP port is available on localhost.

    Args:
        port: Port to check

    Returns:
        True if available, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(0.2)
        result = sock.connect_ex(("127.0.0.1", port))
        return result != 0


def find_available_port(start_port: int, max_increment: int = 10) -> int:
    """Find an available port, scanning upward from start_port.

    Args:
        start_port: Port to start checking from
        max_increment: How many ports to scan upward at most

    Returns:
        First available port found

    Raises:
        RuntimeError: If no port is available in the range
    """
    port = start_port
    upper_bound = start_port + max_increment
    while port <= upper_bound:
        if is_port_available(port):
            return port
        port += 1
    raise RuntimeError(f"Could not find available port in range {start_port}-{upper_bound}")


def read_env_file(env_path: Path) -> dict[str, str]:
    """Parse a .env file into a simple key/value mapping.

    Args:
        env_path: Path to .env file

    Returns:
        Mapping of keys to unquoted string values
    """
    result: dict[str, str] = {}
    if not env_path.exists():
        return result
    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_val = line.split("=", 1)
        val = raw_val.strip()
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        result[key.strip()] = val
    return result


def ensure_virtualenv(project_root: Path) -> None:
    """Verify that a local virtual environment exists (parity with bash script)."""
    if not (project_root / ".venv").exists():
        print(
            "[ERROR] Virtual environment not found. Please run ./scripts/check-prerequisites.sh first",
            file=sys.stderr,
        )
        sys.exit(1)


def validate_env_values(env_values: dict[str, str]) -> None:
    """Validate required environment variables similar to the bash script.

    - GOOGLE_API_KEY must be set and not the placeholder
    - SPLUNK_MCP_SERVER_URL must be set
    """
    google_api_key = env_values.get("GOOGLE_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    if not google_api_key or google_api_key == "your-google-ai-studio-api-key":
        print("[ERROR] GOOGLE_API_KEY not configured in .env file", file=sys.stderr)
        sys.exit(1)

    mcp_url = env_values.get("SPLUNK_MCP_SERVER_URL", "") or os.environ.get(
        "SPLUNK_MCP_SERVER_URL", ""
    )
    if not mcp_url:
        print("[ERROR] SPLUNK_MCP_SERVER_URL not configured in .env file", file=sys.stderr)
        sys.exit(1)


def ensure_mcp_reachable(mcp_url: str) -> None:
    """Check MCP server reachability (HTTP GET), exit with guidance if unreachable."""
    try:
        # Short timeout, we only need to see it's listening
        with httpx.Client(timeout=5.0, follow_redirects=True) as client:
            client.get(mcp_url)
    except httpx.RequestError:
        print("[ERROR] ❌ MCP server not reachable at", mcp_url, file=sys.stderr)
        print("\n🔧 Please start the MCP server before continuing:\n", file=sys.stderr)
        print("   For mcp-server-for-splunk:", file=sys.stderr)
        print("   cd ../mcp-server-for-splunk", file=sys.stderr)
        print("   uv run fastmcp run src/server.py --transport http --port 8001", file=sys.stderr)
        print("   OR ./scripts/build_and_run.sh --local", file=sys.stderr)
        print("\n   Then re-run this command.\n", file=sys.stderr)
        sys.exit(1)


def wait_for_http(port: int, attempts: int = 10, delay_seconds: float = 3.0) -> bool:
    """Wait for a local HTTP endpoint to respond by opening a TCP connection.

    Args:
        port: Local port to probe
        attempts: Number of attempts
        delay_seconds: Delay between attempts

    Returns:
        True if connection succeeds, False otherwise
    """
    for _ in range(attempts):
        if not is_port_available(port):
            return True
        time.sleep(delay_seconds)
    return False


def main() -> None:
    """Entry point to start ADK web, cross-OS, with parity to bash script."""
    project_root = find_project_root()
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Ensure no previous instance (best-effort): call our stop-lab entry if available
    try:
        # Use this same interpreter to invoke package entry
        subprocess.run(
            [sys.executable, "-m", "ai_sidekick_for_splunk.cli.stop_lab"],
            cwd=str(project_root),
            check=False,
        )
    except OSError:
        pass

    # Environment checks: venv presence, .env existence and values, MCP reachability
    ensure_virtualenv(project_root)
    env_path = project_root / ".env"
    if not env_path.exists():
        print("[ERROR] .env file not found. Please run setup-env first.", file=sys.stderr)
        sys.exit(1)
    env_values = read_env_file(env_path)
    validate_env_values(env_values)

    mcp_url = env_values.get("SPLUNK_MCP_SERVER_URL", os.environ.get("SPLUNK_MCP_SERVER_URL", ""))
    if mcp_url:
        ensure_mcp_reachable(mcp_url)

    # Choose port
    try:
        sidekick_port = find_available_port(8087, max_increment=10)
    except RuntimeError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    # Start ADK web
    # Note: assumes 'adk' is on PATH in the project's environment
    start_cmd = ["adk", "web", "--port", str(sidekick_port)]
    child_env = os.environ.copy()
    child_env["PORT"] = str(sidekick_port)  # parity with bash script export
    proc = subprocess.Popen(start_cmd, cwd=str(project_root / "src"), env=child_env)

    # Save PID
    (logs_dir / "ai-sidekick.pid").write_text(str(proc.pid))

    # Wait and verify port is bound
    if not wait_for_http(sidekick_port, attempts=10, delay_seconds=3.0):
        print("[WARN] ADK agent may still be starting... check manually", file=sys.stderr)

    print(f"ADK agent attempted start on port {sidekick_port}")
    print(f"Web interface: http://localhost:{sidekick_port}")
    dev_ui_url = f"http://127.0.0.1:{sidekick_port}/dev-ui/?app=ai_sidekick_for_splunk"
    print(f"Dev UI (agent preselected): {dev_ui_url}")

    # Best-effort attempt to open the Dev UI in the default browser
    try:
        webbrowser.open(dev_ui_url, new=2)
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
