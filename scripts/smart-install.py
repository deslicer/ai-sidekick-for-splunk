#!/usr/bin/env python3
"""
AI Sidekick for Splunk - Installation Script
Verifies system requirements and installs missing dependencies
Ensures UV package manager and Git are available for project setup
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for cross-platform colored output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    WHITE = '\033[1;37m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    @classmethod
    def disable(cls):
        """Disable colors for non-terminal output"""
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = ''
        cls.CYAN = cls.MAGENTA = cls.WHITE = cls.RESET = cls.BOLD = ''


class PrerequisiteChecker:
    """Installation script for AI Sidekick for Splunk"""

    def __init__(self, verbose: bool = False, json_output: bool = False, check_only: bool = False):
        self.verbose = verbose
        self.json_output = json_output
        self.check_only = check_only
        self.missing_requirements = []
        self.optional_missing = []
        self.installation_tips = []
        self.results = {}
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / '.venv'

        # Detect if we're in a terminal for color support
        if not sys.stdout.isatty() or os.getenv('NO_COLOR') or json_output:
            Colors.disable()

        # Emoji support based on platform and locale
        self.use_emoji = self._detect_emoji_support()

    def _detect_emoji_support(self) -> bool:
        """Detect if terminal supports emoji"""
        if platform.system() == 'Windows':
            # Windows Terminal and newer CMD support emoji
            return os.getenv('WT_SESSION') is not None or sys.version_info >= (3, 7)
        return True  # Most Unix terminals support emoji

    def _get_emoji(self, emoji_type: str) -> str:
        """Get emoji or fallback text"""
        emojis = {
            'success': '✅' if self.use_emoji else '[OK]',
            'warning': '⚠️ ' if self.use_emoji else '[WARN]',
            'error': '❌' if self.use_emoji else '[ERR]',
            'info': 'ℹ️ ' if self.use_emoji else '[INFO]',
            'search': '🔍' if self.use_emoji else '[CHECK]',
            'tools': '🔧' if self.use_emoji else '[TOOLS]',
            'system': '💻' if self.use_emoji else '[SYSTEM]',
            'rocket': '🚀' if self.use_emoji else '[READY]',
            'package': '📦' if self.use_emoji else '[INSTALL]',
        }
        return emojis.get(emoji_type, '')

    def print_success(self, message: str):
        """Print success message"""
        if not self.json_output:
            print(f"{Colors.GREEN}{self._get_emoji('success')} {message}{Colors.RESET}")

    def print_warning(self, message: str):
        """Print warning message"""
        if not self.json_output:
            print(f"{Colors.YELLOW}{self._get_emoji('warning')} {message}{Colors.RESET}")

    def print_error(self, message: str):
        """Print error message"""
        if not self.json_output:
            print(f"{Colors.RED}{self._get_emoji('error')} {message}{Colors.RESET}")

    def print_info(self, message: str):
        """Print info message"""
        if not self.json_output:
            print(f"{Colors.BLUE}{self._get_emoji('info')} {message}{Colors.RESET}")

    def print_header(self, message: str):
        """Print section header"""
        if not self.json_output:
            print(f"\n{Colors.CYAN}{Colors.BOLD}{message}{Colors.RESET}")
            print(f"{Colors.CYAN}{'=' * len(message.replace(self._get_emoji('search'), '').replace(self._get_emoji('tools'), '').replace(self._get_emoji('system'), '').strip())}{Colors.RESET}")

    def run_command(self, command: list[str], timeout: int = 10) -> tuple[bool, str, str]:
        """Run command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=platform.system() == 'Windows'
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False, "", "Command not found or timed out"

    def setup_project_environment(self) -> bool:
        """Setup project environment with UV"""
        if self.check_only:
            return True
            
        if not self.json_output:
            self.print_info("Setting up project environment...")
            
        # Check if pyproject.toml exists
        if not Path("pyproject.toml").exists():
            if not self.json_output:
                self.print_warning("No pyproject.toml found - skipping environment setup")
                self.print_info("Make sure you're running this script from the project root directory")
            return True
            
        if not self.json_output:
            self.print_info("Creating virtual environment and installing dependencies...")
            
        try:
            # Run uv sync to create venv and install dependencies
            success, stdout, stderr = self.run_command(['uv', 'sync'], timeout=120)
            if success:
                if not self.json_output:
                    self.print_success("Virtual environment created and dependencies installed")
                    if self.verbose:
                        self.print_info("    Virtual environment location: .venv/")
                        
                # Verify the environment works
                venv_python = self.get_venv_python()
                if Path(venv_python).exists():
                    if not self.json_output:
                        self.print_success("Virtual environment ready")
                else:
                    if not self.json_output:
                        self.print_warning("Virtual environment created but Python executable not found")
                return True
            else:
                if not self.json_output:
                    self.print_error("Failed to create virtual environment or install dependencies")
                    self.print_info("You may need to run 'uv sync' manually in the project directory")
                return False
        except Exception as e:
            if not self.json_output:
                self.print_error(f"Error setting up project environment: {e}")
            return False

    def check_uv_package_manager(self) -> bool:
        """Check if uv package manager is installed and setup project environment"""
        if shutil.which('uv'):
            success, stdout, _ = self.run_command(['uv', '--version'])
            if success:
                self.print_success(f"UV Package Manager: {stdout}")
                if self.verbose:
                    self.print_info(f"    Location: {shutil.which('uv')}")
                    
                # Verify UV can manage Python versions
                if self.verbose:
                    self.print_info("    Verifying UV Python management capabilities...")
                    
                success_python, _, _ = self.run_command(['uv', 'python', 'list'])
                if success_python:
                    self.print_success("UV Python management available")
                    if self.verbose:
                        self.print_info("    Can automatically download required Python versions")
                else:
                    self.print_info("UV ready to download Python versions as needed")
                    
                self.results['uv'] = {'status': 'ok', 'version': stdout, 'path': shutil.which('uv')}
                
                # Setup project environment
                if not self.json_output:
                    print()  # Add spacing
                env_success = self.setup_project_environment()
                return env_success
            
        self.print_error("UV Package Manager: Not installed")
        self.missing_requirements.append("UV Package Manager")
        self.results['uv'] = {'status': 'missing'}
        return False

    def check_git(self) -> bool:
        """Check if Git is installed"""
        if shutil.which('git'):
            success, stdout, _ = self.run_command(['git', '--version'])
            if success:
                self.print_success(f"Git: {stdout}")
                if self.verbose:
                    self.print_info(f"    Location: {shutil.which('git')}")
                self.results['git'] = {'status': 'ok', 'version': stdout, 'path': shutil.which('git')}
                return True

        self.print_error("Git: Not found")
        self.missing_requirements.append("Git")
        self.results['git'] = {'status': 'missing'}
        
        # Show installation instructions
        if not self.json_output:
            if platform.system() == 'Darwin':  # macOS
                self.print_info("Installation options:")
                print("  1. brew install git")
                print("  2. xcode-select --install") 
                print("  3. https://git-scm.com")
            elif platform.system() == 'Windows':
                self.print_info("Installation options:")
                print("  1. winget install Git.Git")
                print("  2. choco install git")
                print("  3. scoop install git")
                print("  4. https://git-scm.com")
            else:  # Linux
                self.print_info("Install: Use your distribution's package manager")
                print("  Examples: sudo apt install git, sudo dnf install git")
        return False


    def check_optional_tools(self):
        """Check for optional development tools"""
        if not self.json_output:
            self.print_header(f"{self._get_emoji('tools')} Optional Tools")
            
        # Node.js for MCP Inspector
        if shutil.which('node'):
            success, stdout, _ = self.run_command(['node', '--version'])
            if success:
                self.print_success(f"Node.js: {stdout}")
            else:
                self.print_success("Node.js found")
        else:
            self.print_info("Node.js: Not found (optional)")
            
        # Docker for containerization  
        if shutil.which('docker'):
            success, stdout, _ = self.run_command(['docker', '--version'])
            if success:
                self.print_success(f"Docker: {stdout}")
            else:
                self.print_success("Docker found")
        else:
            self.print_info("Docker: Not found (optional)")

    def get_system_info(self) -> dict[str, str]:
        """Get comprehensive system information"""
        info = {
            'os': platform.system(),
            'os_version': platform.release(),
            'architecture': platform.machine(),
            'python_version': platform.python_version(),
            'platform': platform.platform(),
        }

        # OS-specific information
        if platform.system() == 'Windows':
            info['windows_version'] = platform.win32_ver()[0]
            info['windows_edition'] = platform.win32_edition()
        elif platform.system() == 'Darwin':
            info['macos_version'] = platform.mac_ver()[0]
        elif platform.system() == 'Linux':
            try:
                with open('/etc/os-release') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            info['linux_distro'] = line.split('=', 1)[1].strip().strip('"')
                            break
            except FileNotFoundError:
                pass

        return info

    def detect_package_manager(self) -> tuple[str, list[str]]:
        """Detect available package manager and return install commands"""
        system = platform.system()

        if system == 'Windows':
            if shutil.which('winget'):
                return 'winget', [
                    'winget install Python.Python.3.11 Git.Git',
                    'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
                ]
            elif shutil.which('choco'):
                return 'chocolatey', [
                    'choco install python311 git',
                    'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
                ]
            else:
                return 'manual', [
                    '# Download and install Python 3.11+ from python.org',
                    '# Download and install Git from git-scm.com',
                    '# Install uv: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
                ]

        elif system == 'Darwin':  # macOS
            if shutil.which('brew'):
                return 'homebrew', [
                    'brew install python@3.11 git uv'
                ]
            elif shutil.which('port'):
                return 'macports', [
                    'sudo port install python311 git',
                    'curl -LsSf https://astral.sh/uv/install.sh | sh'
                ]
            else:
                return 'manual', [
                    '# Install Homebrew: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                    'brew install python@3.11 git uv'
                ]

        else:  # Linux and others
            managers = [
                ('apt', ['sudo apt update && sudo apt install -y python3.11 python3.11-pip python3.11-venv git curl']),
                ('dnf', ['sudo dnf install -y python3.11 python3.11-pip git curl']),
                ('yum', ['sudo yum install -y python3.11 python3.11-pip git curl']),
                ('pacman', ['sudo pacman -S python git curl']),
                ('zypper', ['sudo zypper install python311 git curl']),
            ]

            for manager, commands in managers:
                if shutil.which(manager):
                    commands.append('curl -LsSf https://astral.sh/uv/install.sh | sh')
                    return manager, commands

            return 'manual', [
                '# Install Python 3.11+, Git, and curl using your distribution\'s package manager',
                'curl -LsSf https://astral.sh/uv/install.sh | sh'
            ]





    def get_venv_python(self) -> str:
        """Get the path to Python in the virtual environment"""
        if platform.system() == 'Windows':
            return str(self.venv_path / 'Scripts' / 'python.exe')
        else:
            return str(self.venv_path / 'bin' / 'python')

    def run_checks(self) -> bool:
        """Run all prerequisite checks"""
        if not self.json_output:
            print(f"{Colors.CYAN}{self._get_emoji('search')} Checking Prerequisites for AI Sidekick for Splunk...{Colors.RESET}")
            print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")

        # Required checks
        self.print_header(f"{self._get_emoji('tools')} Required Components")

        checks = [
            ("UV Package Manager", self.check_uv_package_manager),
            ("Git", self.check_git),
        ]

        all_passed = True
        for name, check_func in checks:
            try:
                result = check_func()
                all_passed = all_passed and result
            except Exception as e:
                self.print_error(f"{name}: Check failed - {e}")
                all_passed = False

        # Optional tools check
        if all_passed:
            self.check_optional_tools()

        # System information
        if self.verbose:
            self.print_header(f"{self._get_emoji('system')} System Information")
            system_info = self.get_system_info()
            for key, value in system_info.items():
                self.print_info(f"{key.replace('_', ' ').title()}: {value}")

        return all_passed

    def print_summary(self, all_passed: bool):
        """Print summary and next steps"""
        if self.json_output:
            summary = {
                'all_requirements_met': all_passed,
                'missing_requirements': self.missing_requirements,
                'optional_missing': self.optional_missing,
                'results': self.results,
                'system_info': self.get_system_info()
            }
            print(json.dumps(summary, indent=2))
            return

        self.print_header("📊 Summary")

        if all_passed:
            self.print_success("UV Package Manager available")
            self.print_success("Git version control available")
            self.print_success("System ready for setup")
            print()
            self.print_header("🚀 Ready to Start")
            print("1. Activate the virtual environment:")
            if platform.system() == 'Windows':
                print("   .venv\\Scripts\\activate")
            else:
                print("   source .venv/bin/activate")
            print("2. Start AI Sidekick: uv run ai-sidekick --start")
            print("3. Access web interface: http://localhost:8087")
            print()
            self.print_info("Virtual environment and dependencies are ready!")
        else:
            self.print_error(f"Missing required tools: {', '.join(self.missing_requirements)}")
            print()
            self.print_header("📋 Installation Commands")

            package_manager, install_commands = self.detect_package_manager()

            if package_manager != 'manual':
                self.print_info(f"Detected package manager: {package_manager}")
                print()

            for cmd in install_commands:
                if cmd.startswith('#'):
                    print(f"{Colors.CYAN}{cmd}{Colors.RESET}")
                else:
                    print(f"{Colors.WHITE}{cmd}{Colors.RESET}")

            print()
            self.print_header("🔄 After Installation")
            print(f"{Colors.CYAN}Run this script again to verify installation:{Colors.RESET}")
            print(f"{Colors.WHITE}python scripts/smart-install.py{Colors.RESET}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Sidekick for Splunk - Installation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/smart-install.py            # Check and setup environment
    python scripts/smart-install.py --verbose  # Show detailed information
    python scripts/smart-install.py --check-only # Only check, don't install
    python scripts/smart-install.py --json     # JSON output for automation

Requirements:
    - UV package manager (handles Python and dependencies automatically)
    - Git (for repository operations)
        """
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show verbose output with version information and installation paths'
    )

    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output results in JSON format for automation'
    )

    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check prerequisites without installing anything'
    )



    args = parser.parse_args()

    checker = PrerequisiteChecker(verbose=args.verbose, json_output=args.json, check_only=args.check_only)

    try:
        all_passed = checker.run_checks()
        checker.print_summary(all_passed)

        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)

    except KeyboardInterrupt:
        if not args.json:
            print(f"\n{Colors.YELLOW}Check interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        if args.json:
            print(json.dumps({'error': str(e), 'success': False}))
        else:
            print(f"{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == '__main__':
    main()
