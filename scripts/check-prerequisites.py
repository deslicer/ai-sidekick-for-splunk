#!/usr/bin/env python3
"""
Prerequisites Checker for AI Sidekick for Splunk
Cross-platform script to verify and install required dependencies
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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
    """Cross-platform prerequisites checker for AI Sidekick for Splunk"""

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

    def run_command(self, command: List[str], timeout: int = 10) -> Tuple[bool, str, str]:
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

    def check_python_version(self) -> bool:
        """Check if Python 3.11+ is available"""
        try:
            # Check current Python version
            current_version = sys.version_info
            if current_version >= (3, 11):
                version_str = f"{current_version.major}.{current_version.minor}.{current_version.micro}"
                self.print_success(f"Python: {version_str} (current interpreter)")
                if self.verbose:
                    self.print_info(f"    Location: {sys.executable}")
                self.results['python'] = {'status': 'ok', 'version': version_str, 'path': sys.executable}
                return True

            # Check if python3.11+ is available in PATH
            for python_cmd in ['python3.11', 'python3.12', 'python3.13', 'python3']:
                if shutil.which(python_cmd):
                    success, stdout, _ = self.run_command([python_cmd, '--version'])
                    if success and 'Python 3.1' in stdout:
                        version_parts = stdout.replace('Python ', '').split('.')
                        if len(version_parts) >= 2 and int(version_parts[1]) >= 11:
                            self.print_success(f"Python: {stdout}")
                            if self.verbose:
                                self.print_info(f"    Location: {shutil.which(python_cmd)}")
                            self.results['python'] = {'status': 'ok', 'version': stdout, 'path': shutil.which(python_cmd)}
                            return True

            # Python 3.11+ not found
            self.print_error("Python 3.11+: Not found")
            self.missing_requirements.append("Python 3.11+")
            self.results['python'] = {'status': 'missing', 'required': '3.11+'}
            return False

        except Exception as e:
            self.print_error(f"Python check failed: {e}")
            self.results['python'] = {'status': 'error', 'error': str(e)}
            return False

    def check_uv_package_manager(self) -> bool:
        """Check if uv package manager is installed"""
        if shutil.which('uv'):
            success, stdout, _ = self.run_command(['uv', '--version'])
            if success:
                self.print_success(f"UV Package Manager: {stdout}")
                if self.verbose:
                    self.print_info(f"    Location: {shutil.which('uv')}")
                self.results['uv'] = {'status': 'ok', 'version': stdout, 'path': shutil.which('uv')}
                return True

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

        self.print_error("Git: Not installed")
        self.missing_requirements.append("Git")
        self.results['git'] = {'status': 'missing'}
        return False





    def get_system_info(self) -> Dict[str, str]:
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

    def detect_package_manager(self) -> Tuple[str, List[str]]:
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

    def check_uv_environment_conflicts(self) -> bool:
        """Check for UV environment conflicts and automatically clean them up for lab environment"""
        uv_env_path = os.getenv('UV_ENVIRONMENT_PATH')

        if uv_env_path:
            if not self.json_output:
                self.print_warning(f"UV_ENVIRONMENT_PATH was set: {uv_env_path}")
                self.print_info("    Automatically unsetting for clean lab environment...")

            # Automatically unset for lab environment
            del os.environ['UV_ENVIRONMENT_PATH']

            if not self.json_output:
                self.print_success("UV_ENVIRONMENT_PATH cleared successfully")

            return True

        if not self.json_output:
            self.print_success("UV environment: Clean (no conflicts)")
        return True

    def deactivate_current_env(self) -> bool:
        """Deactivate any currently active virtual environment"""
        if not self.check_only:
            # Check if we're in a virtual environment
            if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                if not self.json_output:
                    self.print_info("Deactivating current virtual environment...")

                # Clear environment variables that indicate active venv
                env_vars_to_clear = ['VIRTUAL_ENV', 'UV_ENVIRONMENT_PATH', 'CONDA_DEFAULT_ENV']
                for var in env_vars_to_clear:
                    if var in os.environ:
                        if not self.json_output:
                            self.print_info(f"    Clearing {var}")
                        del os.environ[var]

                # Reset Python path to system Python
                if not self.json_output:
                    self.print_success("Virtual environment deactivated")
                return True
            else:
                if not self.json_output:
                    self.print_info("No active virtual environment to deactivate")
                return True
        return True

    def create_project_venv(self) -> bool:
        """Create project-local virtual environment"""
        if not self.check_only:
            # First deactivate any current environment
            self.deactivate_current_env()

            if not self.json_output:
                self.print_info(f"Creating virtual environment at {self.venv_path}")

            try:
                # Create virtual environment
                success, stdout, stderr = self.run_command(['uv', 'venv', str(self.venv_path)], timeout=30)
                if success:
                    if not self.json_output:
                        self.print_success("Virtual environment created successfully")
                    return True
                else:
                    if not self.json_output:
                        self.print_error(f"Failed to create virtual environment: {stderr}")
                    return False
            except Exception as e:
                if not self.json_output:
                    self.print_error(f"Error creating virtual environment: {e}")
                return False
        return True

    def get_venv_python(self) -> str:
        """Get the path to Python in the virtual environment"""
        if platform.system() == 'Windows':
            return str(self.venv_path / 'Scripts' / 'python.exe')
        else:
            return str(self.venv_path / 'bin' / 'python')

    def get_venv_pip(self) -> str:
        """Get the path to pip in the virtual environment"""
        if platform.system() == 'Windows':
            return str(self.venv_path / 'Scripts' / 'pip.exe')
        else:
            return str(self.venv_path / 'bin' / 'pip')

    def install_dependencies(self) -> bool:
        """Install required dependencies in the virtual environment"""
        if self.check_only:
            return True

        if not self.venv_path.exists():
            if not self.json_output:
                self.print_error("Virtual environment not found. Creating it first...")
            if not self.create_project_venv():
                return False

        if not self.json_output:
            self.print_info("Installing dependencies in virtual environment...")

        try:
            # Install Google ADK
            success, stdout, stderr = self.run_command([
                'uv', 'pip', 'install', '--python', self.get_venv_python(),
                'google-adk>=1.11.0'
            ], timeout=120)

            if success:
                if not self.json_output:
                    self.print_success("Google ADK installed successfully")
            else:
                if not self.json_output:
                    self.print_error(f"Failed to install Google ADK: {stderr}")
                return False

            # Install project in editable mode
            success, stdout, stderr = self.run_command([
                'uv', 'pip', 'install', '--python', self.get_venv_python(),
                '-e', '.'
            ], timeout=60)

            if success:
                if not self.json_output:
                    self.print_success("Project installed in editable mode")
                return True
            else:
                if not self.json_output:
                    self.print_error(f"Failed to install project: {stderr}")
                return False

        except Exception as e:
            if not self.json_output:
                self.print_error(f"Error installing dependencies: {e}")
            return False



    def generate_setup_commands(self) -> List[str]:
        """Generate setup commands after prerequisites are met"""
        commands = []

        if platform.system() == 'Windows':
            commands.extend([
                '# Navigate to project root directory',
                'cd /path/to/ai-sidekick-for-splunk',
                '',
                '# Create project-local virtual environment',
                'uv venv .venv',
                'uv pip install --upgrade pip',
                '',
                '# Install project dependencies',
                'uv pip install google-adk>=1.11.0',
                'uv pip install -e .',
                '',
                '# Activate the environment for future sessions',
                '.venv\\Scripts\\activate',
                '',
                '# Set up environment variables using setup script',
                'python scripts/lab/setup-env.sh',
                '',
                '# Test the setup',
                'python -c "import google.adk; print(\'Google ADK installed successfully\')"'
            ])
        else:
            commands.extend([
                '# Navigate to project root directory',
                'cd /path/to/ai-sidekick-for-splunk',
                '',
                '# Create project-local virtual environment',
                'uv venv .venv',
                'source .venv/bin/activate',
                'uv pip install --upgrade pip',
                '',
                '# Install project dependencies',
                'uv pip install google-adk>=1.11.0',
                'uv pip install -e .',
                '',
                '# Set up environment variables using setup script',
                './scripts/lab/setup-env.sh',
                '',
                '# Test the setup',
                'python -c "import google.adk; print(\'Google ADK installed successfully\')"'
            ])

        return commands

    def auto_setup(self) -> bool:
        """Automatically set up the project environment"""
        if self.check_only:
            return True

        if not self.json_output:
            self.print_header(f"{self._get_emoji('rocket')} Automatic Setup")

        setup_success = True

        # Step 1: Create project virtual environment if it doesn't exist
        if not self.venv_path.exists():
            if not self.json_output:
                self.print_info("Project virtual environment not found. Creating...")
            if not self.create_project_venv():
                setup_success = False
        else:
            if not self.json_output:
                self.print_success("Project virtual environment already exists")

        # Step 2: Install dependencies
        if setup_success:
            if not self.json_output:
                self.print_info("Installing/updating dependencies...")
            if not self.install_dependencies():
                setup_success = False



        if setup_success and not self.json_output:
            self.print_success("Automatic setup completed successfully!")
            self.print_info("")
            self.print_info("🎉 Project environment is ready!")

            # Print setup summary
            self.print_header("Setup Summary")
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            self.print_info(f"[SUCCESS] ✅ Python {python_version}")
            self.print_info(f"[SUCCESS] ✅ uv package manager")
            self.print_info(f"[SUCCESS] ✅ Git version control")
            self.print_info(f"[SUCCESS] ✅ Virtual environment created at .venv/")
            self.print_info(f"[SUCCESS] ✅ Google ADK installed")
            self.print_info(f"[SUCCESS] ✅ Core dependencies installed")

            self.print_info("")
            self.print_header("🚀 Next Steps")

            if platform.system() == 'Windows':
                self.print_info("1. Activate the virtual environment:")
                self.print_info("   .venv\\Scripts\\activate")
            else:
                self.print_info("1. Activate the virtual environment:")
                self.print_info("   source .venv/bin/activate")

            self.print_info("")
            self.print_info("2. Start AI Sidekick - run:")
            self.print_info("   uv run start-lab")

        return setup_success

    def run_checks(self) -> bool:
        """Run all prerequisite checks"""
        if not self.json_output:
            print(f"{Colors.CYAN}{self._get_emoji('search')} Checking Prerequisites for AI Sidekick for Splunk...{Colors.RESET}")
            print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")

        # Required checks
        self.print_header(f"{self._get_emoji('tools')} Required Components")

        checks = [
            ("Python 3.11+", self.check_python_version),
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



        # System information
        if self.verbose:
            self.print_header(f"{self._get_emoji('system')} System Information")
            system_info = self.get_system_info()
            for key, value in system_info.items():
                self.print_info(f"{key.replace('_', ' ').title()}: {value}")

        # Run automatic setup if basic requirements are met
        if all_passed and not self.check_only:
            setup_success = self.auto_setup()
            all_passed = all_passed and setup_success

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
            self.print_success("All required prerequisites are installed! 🎉")
            print()
            print(f"{Colors.GREEN}{self._get_emoji('rocket')} Environment is ready!{Colors.RESET}")
        else:
            self.print_error(f"Missing required prerequisites: {', '.join(self.missing_requirements)}")
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
            print(f"{Colors.WHITE}python scripts/check-prerequisites.py{Colors.RESET}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Check prerequisites for AI Sidekick for Splunk",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/check-prerequisites.py            # Check and auto-setup
    python scripts/check-prerequisites.py --verbose  # Verbose output with paths
    python scripts/check-prerequisites.py --check-only # Only check, don't install
    python scripts/check-prerequisites.py --json     # JSON output for automation
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
