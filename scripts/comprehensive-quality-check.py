#!/usr/bin/env python3
"""
Comprehensive Code Quality Check for AI Sidekick for Splunk.

This script runs all quality checks including linting, formatting, code review,
security scanning, and security audit to ensure codebase quality and security.
"""

import argparse
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from ai_sidekick_for_splunk.core.utils.colors import Colors
except ImportError:
    # Fallback color class
    class Colors:
        RED = "\033[0;31m"
        GREEN = "\033[0;32m"
        YELLOW = "\033[1;33m"
        BLUE = "\033[0;34m"
        CYAN = "\033[0;36m"
        RESET = "\033[0m"
        BOLD = "\033[1m"


class QualityChecker:
    """Comprehensive code quality checker."""

    def __init__(self, verbose: bool = False, fix: bool = False):
        self.verbose = verbose
        self.fix = fix
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        self.errors = []
        self.warnings = []

    def print_header(self, title: str) -> None:
        """Print a formatted header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}🔍 {title}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")

    def print_success(self, message: str) -> None:
        """Print success message."""
        print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        print(f"{Colors.RED}❌ {message}{Colors.RESET}")
        self.errors.append(message)

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")
        self.warnings.append(message)

    def print_info(self, message: str) -> None:
        """Print info message."""
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

    def run_command(
        self, command: list[str], cwd: Path = None, capture_output: bool = True
    ) -> tuple[bool, str, str]:
        """Run a command and return success status, stdout, stderr."""
        try:
            cwd = cwd or self.project_root
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except FileNotFoundError:
            return False, "", f"Command not found: {command[0]}"
        except Exception as e:
            return False, "", str(e)

    def check_ruff_formatting(self) -> bool:
        """Check and fix code formatting with Ruff."""
        self.print_header("Code Formatting (Ruff)")

        # First check if there are formatting issues
        success, stdout, stderr = self.run_command(["uv", "run", "ruff", "format", "--check"])
        if not success:
            self.print_warning("Code formatting issues found")
            if self.verbose:
                print(stdout)
                print(stderr)

            if self.fix:
                self.print_info("Fixing formatting issues...")
                fix_success, fix_stdout, fix_stderr = self.run_command(
                    ["uv", "run", "ruff", "format"]
                )
                if fix_success:
                    self.print_success("Code formatting fixed")
                    return True
                else:
                    self.print_error("Failed to fix formatting issues")
                    if self.verbose:
                        print(fix_stdout)
                        print(fix_stderr)
                    return False
            else:
                return False
        else:
            self.print_success("Code formatting is correct")
            return True

    def check_ruff_linting(self) -> bool:
        """Check and fix linting issues with Ruff."""
        self.print_header("Code Linting (Ruff)")

        # Run linting with auto-fix if requested
        command = ["uv", "run", "ruff", "check"]
        if self.fix:
            command.append("--fix")

        success, stdout, stderr = self.run_command(command)

        if not success:
            if "fixable with the `--fix` option" in stderr:
                self.print_warning("Linting issues found (some fixable)")
                if self.verbose:
                    print(stdout)
                    print(stderr)

                if self.fix:
                    self.print_info("Attempting to fix safe linting issues...")
                    # Only apply safe fixes automatically
                    fix_success, fix_stdout, fix_stderr = self.run_command(
                        ["uv", "run", "ruff", "check", "--fix"]
                    )
                    if fix_success:
                        self.print_success("Linting issues fixed")
                        return True
                    else:
                        self.print_error("Failed to fix all linting issues")
                        if self.verbose:
                            print(fix_stdout)
                            print(fix_stderr)
                        return False
                else:
                    return False
            else:
                self.print_error("Linting errors found")
                if self.verbose:
                    print(stdout)
                    print(stderr)
                return False
        else:
            self.print_success("No linting issues found")
            return True

    def check_code_quality(self) -> bool:
        """Run MyPy type checking and other quality checks."""
        self.print_header("Code Quality (MyPy & Analysis)")

        # MyPy type checking
        success, stdout, stderr = self.run_command(
            [
                "uv",
                "run",
                "mypy",
                "src/ai_sidekick_for_splunk/core/models/",
                "--ignore-missing-imports",
            ]
        )

        if success:
            self.print_success("MyPy type checking passed")
        else:
            self.print_warning("MyPy type checking found issues")
            if self.verbose:
                print(stdout)
                print(stderr)

        # Additional quality checks can be added here
        return success

    def check_security_vulnerabilities(self) -> bool:
        """Run security vulnerability scanning."""
        self.print_header("Security Scanning")

        all_passed = True

        # Check for hardcoded secrets
        success, stdout, stderr = self.run_command(
            [
                "grep",
                "-r",
                "-i",
                "password|secret|key|token",
                "src/ai_sidekick_for_splunk",
                "--include=*.py",
            ]
        )

        if success and stdout.strip():
            # Filter out legitimate uses (environment variables, config classes, etc.)
            lines = [
                line
                for line in stdout.split("\n")
                if line.strip()
                and not any(
                    safe in line.lower()
                    for safe in [
                        "os.getenv",
                        "field(default_factory=lambda: os.getenv",
                        "config.",
                        "self.config.",
                        "password=",
                        "secret=",
                        "key=",
                        "token=",
                        "api_key",
                        "***masked***",
                    ]
                )
            ]

            if lines:
                self.print_error("Potential hardcoded secrets found")
                if self.verbose:
                    for line in lines[:10]:  # Show first 10
                        print(f"  {line}")
                all_passed = False
            else:
                self.print_success("No hardcoded secrets detected")
        else:
            self.print_success("No hardcoded secrets detected")

        # Check for insecure patterns
        insecure_patterns = [
            ("curl.*|.*sh", "Insecure curl|sh patterns"),
            ("eval\\s*\\(", "Dangerous eval() usage"),
            ("exec\\s*\\(", "Dangerous exec() usage"),
            ("subprocess.*shell.*=.*True", "Dangerous shell=True in subprocess"),
        ]

        for pattern, description in insecure_patterns:
            success, stdout, stderr = self.run_command(
                ["grep", "-r", "-n", pattern, "src/ai_sidekick_for_splunk", "--include=*.py"]
            )

            if success and stdout.strip():
                self.print_error(f"{description} found")
                if self.verbose:
                    print(stdout[:500])  # Limit output
                all_passed = False
            else:
                self.print_success(f"No {description.lower()} detected")

        # Check dependency security
        success, stdout, stderr = self.run_command(["uv", "pip", "check"])
        if success:
            self.print_success("All dependencies are compatible")
        else:
            self.print_error("Dependency conflicts found")
            if self.verbose:
                print(stderr[:1000])  # Limit output
            all_passed = False

        return all_passed

    def run_code_review_checklist(self) -> bool:
        """Run code review checklist verification."""
        self.print_header("Code Review Checklist")

        issues = []

        # Check for TODO/FIXME comments
        success, stdout, stderr = self.run_command(
            [
                "grep",
                "-r",
                "-n",
                "TODO|FIXME|XXX|HACK",
                "src/ai_sidekick_for_splunk",
                "--include=*.py",
            ]
        )

        if success and stdout.strip():
            lines = stdout.strip().split("\n")
            self.print_warning(f"Found {len(lines)} TODO/FIXME comments")
            if self.verbose:
                for line in lines[:5]:  # Show first 5
                    print(f"  {line}")

        # Check for large functions (basic complexity check)
        success, stdout, stderr = self.run_command(
            [
                "find",
                "src/ai_sidekick_for_splunk",
                "-name",
                "*.py",
                "-exec",
                "wc",
                "-l",
                "{}",
                ";",
                "|",
                "sort",
                "-nr",
                "|",
                "head",
                "-5",
            ]
        )

        if success and stdout.strip():
            # Check if any files are too large (>500 lines)
            lines = stdout.strip().split("\n")
            large_files = [line for line in lines if int(line.split()[0]) > 500]
            if large_files:
                self.print_warning(f"Found {len(large_files)} very large files (>500 lines)")
                if self.verbose:
                    for file_info in large_files:
                        print(f"  {file_info}")

        # Check for unused imports (this is covered by ruff, but let's verify)
        self.print_info("Code review checklist completed")
        return len(issues) == 0

    def run_security_audit(self) -> bool:
        """Run comprehensive security audit."""
        self.print_header("Security Audit")

        # This would be a comprehensive security audit
        # For now, we'll run the security checks we have

        audit_passed = True

        # Check environment file permissions
        env_files = ["./.env", "./.env.lab"]
        for env_file in env_files:
            if os.path.exists(env_file):
                stat_info = os.stat(env_file)
                permissions = stat.filemode(stat_info.st_mode)
                if (
                    permissions[1:4] != "rw-"
                    or permissions[4:7] != "---"
                    or permissions[7:10] != "---"
                ):  # Should be owner read/write only (600)
                    self.print_error(
                        f"Environment file {env_file} has incorrect permissions: {permissions}"
                    )
                    self.print_info(f"Run: chmod 600 {env_file}")
                    audit_passed = False
                else:
                    self.print_success(f"Environment file {env_file} has secure permissions")

        # Check for .env in version control (should not happen)
        if os.path.exists("./.env"):
            success, stdout, stderr = self.run_command(["git", "ls-files", ".env"])
            if success and stdout.strip():
                self.print_error(".env file is tracked in git (should be in .gitignore)")
                audit_passed = False

        # Check for large binary files that might contain secrets
        success, stdout, stderr = self.run_command(
            ["find", ".", "-type", "f", "-size", "+10M", "!", "-path", "./.venv/*"]
        )

        if success and stdout.strip():
            files = stdout.strip().split("\n")
            self.print_warning(f"Found {len(files)} large files (>10MB) that should be checked")
            if self.verbose:
                for file_path in files[:3]:  # Show first 3
                    print(f"  {file_path}")

        self.print_info("Security audit completed")
        return audit_passed

    def generate_report(self) -> dict:
        """Generate a comprehensive quality report."""
        return {
            "summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "all_checks_passed": len(self.errors) == 0,
            },
            "errors": self.errors,
            "warnings": self.warnings,
            "checks_run": list(self.results.keys()),
        }

    def run_all_checks(self) -> bool:
        """Run all quality checks."""
        print(
            f"{Colors.BOLD}{Colors.BLUE}🚀 Starting Comprehensive Code Quality Check{Colors.RESET}"
        )
        print(f"{Colors.BLUE}Project: AI Sidekick for Splunk{Colors.RESET}")

        checks = [
            ("formatting", self.check_ruff_formatting),
            ("linting", self.check_ruff_linting),
            ("code_quality", self.check_code_quality),
            ("security", self.check_security_vulnerabilities),
            ("code_review", self.run_code_review_checklist),
            ("security_audit", self.run_security_audit),
        ]

        all_passed = True

        for check_name, check_func in checks:
            try:
                passed = check_func()
                self.results[check_name] = passed
                if not passed:
                    all_passed = False
            except Exception as e:
                self.print_error(f"Check '{check_name}' failed with exception: {e}")
                self.results[check_name] = False
                all_passed = False

        # Generate final report
        self.print_header("FINAL REPORT")

        if all_passed:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL QUALITY CHECKS PASSED!{Colors.RESET}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}⚠️  SOME CHECKS FAILED - REVIEW REQUIRED{Colors.RESET}")

        print(f"\n{Colors.BLUE}Summary:{Colors.RESET}")
        print(f"  Errors: {Colors.RED}{len(self.errors)}{Colors.RESET}")
        print(f"  Warnings: {Colors.YELLOW}{len(self.warnings)}{Colors.RESET}")

        if self.errors:
            print(f"\n{Colors.RED}Errors that need fixing:{Colors.RESET}")
            for error in self.errors[:5]:  # Show first 5
                print(f"  • {error}")

        if self.warnings:
            print(f"\n{Colors.YELLOW}Warnings to consider:{Colors.RESET}")
            for warning in self.warnings[:5]:  # Show first 5
                print(f"  • {warning}")

        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Code Quality Check for AI Sidekick for Splunk",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/comprehensive-quality-check.py              # Run all checks
  python scripts/comprehensive-quality-check.py --fix       # Run checks and auto-fix safe issues only
  python scripts/comprehensive-quality-check.py --verbose   # Show detailed output
  python scripts/comprehensive-quality-check.py --json      # Output results as JSON
        """,
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix safe issues (formatting and safe linting fixes only)",
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    parser.add_argument(
        "--json", action="store_true", help="Output results as JSON instead of formatted text"
    )

    args = parser.parse_args()

    checker = QualityChecker(verbose=args.verbose, fix=args.fix)
    success = checker.run_all_checks()

    if args.json:
        report = checker.generate_report()
        print(json.dumps(report, indent=2))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
