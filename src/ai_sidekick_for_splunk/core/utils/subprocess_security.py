"""
Secure subprocess utilities for AI Sidekick for Splunk.

This module provides secure subprocess execution with input validation,
sanitization, and protection against command injection attacks.
"""

import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)


class SubprocessSecurityError(Exception):
    """Raised when subprocess security validation fails."""

    pass


class SecureSubprocess:
    """
    Secure subprocess execution with input validation and sanitization.

    This class provides methods to safely execute subprocess commands while
    protecting against command injection and other security vulnerabilities.
    """

    # Allowed executables for different contexts
    ALLOWED_EXECUTABLES = {
        "python": ["python", "python3", "python3.11", "python3.12"],
        "system": ["adk", "uv", "git", "curl", "wget"],
        "shell": ["bash", "sh", "zsh", "powershell", "cmd"],
    }

    # Dangerous patterns that should never appear in commands
    DANGEROUS_PATTERNS = [
        r"[;&|`$()]",  # Shell metacharacters
        r"\.\./",  # Directory traversal
        r"rm\s+-rf",  # Dangerous rm commands
        r"sudo\s+rm",  # Dangerous sudo rm
        r">\s*/dev/",  # Writing to device files
        r"<\s*/dev/",  # Reading from device files
    ]

    @classmethod
    def validate_command(cls, command: list[str]) -> None:
        """
        Validate a command for security issues.

        Args:
            command: List of command arguments

        Raises:
            SubprocessSecurityError: If command fails security validation
        """
        if not command:
            raise SubprocessSecurityError("Empty command not allowed")

        executable = command[0]

        # Check if executable is in allowed list
        allowed = False
        for category, executables in cls.ALLOWED_EXECUTABLES.items():
            if executable in executables or any(
                executable.endswith(f"/{exe}") for exe in executables
            ):
                allowed = True
                break

        if not allowed:
            # Allow absolute paths to Python interpreter
            if executable == sys.executable or executable.endswith("/python"):
                allowed = True

        if not allowed:
            raise SubprocessSecurityError(f"Executable '{executable}' not in allowed list")

        # Check for dangerous patterns in all arguments
        full_command = " ".join(command)
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, full_command, re.IGNORECASE):
                raise SubprocessSecurityError(f"Dangerous pattern detected: {pattern}")

        logger.debug(f"Command validation passed: {executable}")

    @classmethod
    def sanitize_environment(cls, env: Optional[dict[str, str]] = None) -> dict[str, str]:
        """
        Sanitize environment variables.

        Args:
            env: Environment variables dict, uses os.environ if None

        Returns:
            Sanitized environment variables
        """
        if env is None:
            env = os.environ.copy()
        else:
            env = env.copy()

        # Remove potentially dangerous environment variables
        dangerous_vars = ["LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES"]
        for var in dangerous_vars:
            env.pop(var, None)

        return env

    @classmethod
    def run_secure(
        cls,
        command: list[str],
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[dict[str, str]] = None,
        timeout: Optional[float] = 30.0,
        check: bool = False,
        capture_output: bool = False,
        text: bool = True,
        **kwargs: Any,
    ) -> subprocess.CompletedProcess:
        """
        Securely run a subprocess command.

        Args:
            command: Command and arguments as list
            cwd: Working directory
            env: Environment variables
            timeout: Command timeout in seconds
            check: Whether to check return code
            capture_output: Whether to capture stdout/stderr
            text: Whether to use text mode
            **kwargs: Additional subprocess.run arguments

        Returns:
            CompletedProcess instance

        Raises:
            SubprocessSecurityError: If security validation fails
            subprocess.TimeoutExpired: If command times out
            subprocess.CalledProcessError: If check=True and command fails
        """
        # Validate command security
        cls.validate_command(command)

        # Sanitize environment
        safe_env = cls.sanitize_environment(env)

        # Convert cwd to string if Path
        if isinstance(cwd, Path):
            cwd = str(cwd)

        # Validate working directory
        if cwd and not os.path.exists(cwd):
            raise SubprocessSecurityError(f"Working directory does not exist: {cwd}")

        logger.info(f"Executing secure subprocess: {command[0]} (args: {len(command) - 1})")
        logger.debug(f"Full command: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=safe_env,
                timeout=timeout,
                check=check,
                capture_output=capture_output,
                text=text,
                **kwargs,
            )

            logger.debug(f"Command completed with return code: {result.returncode}")
            return result

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {command[0]}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with return code {e.returncode}: {command[0]}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error running command {command[0]}: {e}")
            raise

    @classmethod
    def popen_secure(
        cls,
        command: list[str],
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> subprocess.Popen:
        """
        Securely create a subprocess.Popen instance.

        Args:
            command: Command and arguments as list
            cwd: Working directory
            env: Environment variables
            **kwargs: Additional subprocess.Popen arguments

        Returns:
            Popen instance

        Raises:
            SubprocessSecurityError: If security validation fails
        """
        # Validate command security
        cls.validate_command(command)

        # Sanitize environment
        safe_env = cls.sanitize_environment(env)

        # Convert cwd to string if Path
        if isinstance(cwd, Path):
            cwd = str(cwd)

        # Validate working directory
        if cwd and not os.path.exists(cwd):
            raise SubprocessSecurityError(f"Working directory does not exist: {cwd}")

        logger.info(f"Creating secure subprocess: {command[0]} (args: {len(command) - 1})")
        logger.debug(f"Full command: {' '.join(command)}")

        try:
            proc = subprocess.Popen(command, cwd=cwd, env=safe_env, **kwargs)

            logger.debug(f"Process created with PID: {proc.pid}")
            return proc

        except Exception as e:
            logger.error(f"Failed to create process {command[0]}: {e}")
            raise


# Convenience functions for backward compatibility
def run_secure_command(
    command: list[str], cwd: Optional[Union[str, Path]] = None, **kwargs: Any
) -> subprocess.CompletedProcess:
    """
    Convenience function for secure subprocess execution.

    Args:
        command: Command and arguments as list
        cwd: Working directory
        **kwargs: Additional arguments for SecureSubprocess.run_secure

    Returns:
        CompletedProcess instance
    """
    return SecureSubprocess.run_secure(command, cwd=cwd, **kwargs)


def create_secure_process(
    command: list[str], cwd: Optional[Union[str, Path]] = None, **kwargs: Any
) -> subprocess.Popen:
    """
    Convenience function for secure subprocess.Popen creation.

    Args:
        command: Command and arguments as list
        cwd: Working directory
        **kwargs: Additional arguments for SecureSubprocess.popen_secure

    Returns:
        Popen instance
    """
    return SecureSubprocess.popen_secure(command, cwd=cwd, **kwargs)
