#!/bin/bash

# AI Sidekick for Splunk Lab - Prerequisites Installation Script (Unix/Linux/Mac)
# Checks and installs required packages for the Google ADK + MCP + Splunk setup

set -e

# Default options
VERBOSE=false
HELP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Show help if requested
if [[ "$HELP" == "true" ]]; then
    cat << 'EOF'
AI Sidekick for Splunk Lab - Prerequisites Installation Script (Unix/Linux/Mac)

Usage:
    ./scripts/lab/check-prerequisites.sh [options]

Options:
    --verbose, -v     Show detailed version information and installation paths
    --help, -h        Show this help message

Examples:
    ./scripts/lab/check-prerequisites.sh           # Basic check and install
    ./scripts/lab/check-prerequisites.sh --verbose # Detailed information

EOF
    exit 0
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Emoji support check
if command -v locale >/dev/null 2>&1 && [[ "$(locale charmap 2>/dev/null)" == "UTF-8" ]]; then
    EMOJI_SUCCESS="✅"
    EMOJI_WARNING="⚠️ "
    EMOJI_ERROR="❌"
    EMOJI_INFO="ℹ️ "
else
    EMOJI_SUCCESS="[OK]"
    EMOJI_WARNING="[WARN]"
    EMOJI_ERROR="[ERR]"
    EMOJI_INFO="[INFO]"
fi

log_info() {
    echo -e "${BLUE}${EMOJI_INFO} $1${NC}"
}

log_success() {
    echo -e "${GREEN}${EMOJI_SUCCESS} $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}${EMOJI_WARNING} $1${NC}"
}

log_error() {
    echo -e "${RED}${EMOJI_ERROR} $1${NC}"
}

log_step() {
    echo -e "${CYAN}🔧 $1${NC}"
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${CYAN}    $1${NC}"
    fi
}

# Welcome message
echo ""
echo "==========================================================="
echo "🚀 AI Sidekick for Splunk Lab - Prerequisites Check"
echo "   Google ADK + MCP + Splunk Setup"
echo "==========================================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    if command_exists python3; then
        python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
    elif command_exists python; then
        python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
    else
        echo "0.0"
    fi
}

# Function to compare version numbers
version_ge() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Enhanced Python installation with fallbacks
install_python_with_fallbacks() {
    log_info "Python 3.11+ not found. Attempting automatic installation..."
    
    # Detect package manager
    local PACKAGE_MANAGER=""
    if command_exists brew; then
        PACKAGE_MANAGER="brew"
    elif command_exists apt; then
        PACKAGE_MANAGER="apt"
    elif command_exists dnf; then
        PACKAGE_MANAGER="dnf"
    elif command_exists yum; then
        PACKAGE_MANAGER="yum"
    fi
    
    # Method 1: Try package manager first
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        log_info "Trying: brew install python@3.11"
        log_verbose "Using Homebrew package manager"
        if brew install python@3.11 >/dev/null 2>&1; then
            # Update PATH to include new Python
            export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
            log_success "Python 3.11 installed successfully via Homebrew"
            return 0
        else
            log_warning "Homebrew installation failed. Trying alternatives..."
        fi
    elif [[ "$PACKAGE_MANAGER" == "apt" ]]; then
        log_info "Trying: apt install python3.11"
        log_verbose "Using APT package manager"
        if sudo apt update >/dev/null 2>&1 && sudo apt install -y python3.11 python3.11-venv python3.11-pip >/dev/null 2>&1; then
            log_success "Python 3.11 installed successfully via APT"
            return 0
        else
            log_warning "APT installation failed. Trying alternatives..."
        fi
    elif [[ "$PACKAGE_MANAGER" == "dnf" ]]; then
        log_info "Trying: dnf install python3.11"
        log_verbose "Using DNF package manager"
        if sudo dnf install -y python3.11 python3.11-pip >/dev/null 2>&1; then
            log_success "Python 3.11 installed successfully via DNF"
            return 0
        else
            log_warning "DNF installation failed. Trying alternatives..."
        fi
    elif [[ "$PACKAGE_MANAGER" == "yum" ]]; then
        log_info "Trying: yum install python3.11"
        log_verbose "Using YUM package manager"
        if sudo yum install -y python3.11 python3.11-pip >/dev/null 2>&1; then
            log_success "Python 3.11 installed successfully via YUM"
            return 0
        else
            log_warning "YUM installation failed. Trying alternatives..."
        fi
    fi
    
    # Method 2: Try pyenv (if available or can be installed)
    if command_exists pyenv || install_pyenv_fallback; then
        log_info "Trying: pyenv install 3.11"
        log_verbose "Using pyenv Python version manager"
        if pyenv install 3.11.10 >/dev/null 2>&1 && pyenv global 3.11.10 >/dev/null 2>&1; then
            # Update PATH for pyenv
            export PATH="$HOME/.pyenv/bin:$PATH"
            eval "$(pyenv init -)"
            log_success "Python 3.11 installed successfully via pyenv"
            return 0
        else
            log_warning "pyenv installation failed."
        fi
    fi
    
    # All automatic methods failed
    log_error "All automatic Python installation methods failed."
    log_info "Please install Python 3.11+ manually:"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  macOS Options:"
        echo "  1. Official installer: https://www.python.org/downloads/"
        echo "  2. Homebrew: brew install python@3.11"
        echo "  3. pyenv: curl https://pyenv.run | bash && pyenv install 3.11"
        echo "  4. Conda: conda install python=3.11"
    else
        echo "  Linux Options:"
        echo "  1. Official installer: https://www.python.org/downloads/"
        echo "  2. Package manager: $PACKAGE_MANAGER install python3.11"
        echo "  3. pyenv: curl https://pyenv.run | bash && pyenv install 3.11"
        echo "  4. Build from source: https://docs.python.org/3/using/unix.html#building-python"
    fi
    
    return 1
}

# Helper function to install pyenv if possible
install_pyenv_fallback() {
    if command_exists curl; then
        log_info "Installing pyenv..."
        log_verbose "Using pyenv installer via curl"
        if curl https://pyenv.run | bash >/dev/null 2>&1; then
            export PATH="$HOME/.pyenv/bin:$PATH"
            eval "$(pyenv init -)"
            return 0
        fi
    fi
    return 1
}

# Step 1: Check Python
log_step "Checking Python installation..."
PYTHON_VERSION=$(get_python_version)
REQUIRED_VERSION="3.11"

if [[ "$PYTHON_VERSION" == "0.0" ]]; then
    # Try to install Python automatically
    if install_python_with_fallbacks; then
        # Re-check after installation
        PYTHON_VERSION=$(get_python_version)
        if version_ge "$PYTHON_VERSION" "$REQUIRED_VERSION"; then
            log_success "Python $PYTHON_VERSION installed and verified (required: $REQUIRED_VERSION+)"
            if command_exists python3; then
                log_verbose "Location: $(command -v python3)"
            elif command_exists python; then
                log_verbose "Location: $(command -v python)"
            fi
        else
            log_error "Python installation succeeded but version check failed"
            exit 1
        fi
    else
        log_error "Python installation failed. Please install manually."
        exit 1
    fi
elif version_ge "$PYTHON_VERSION" "$REQUIRED_VERSION"; then
    log_success "Python $PYTHON_VERSION found (required: $REQUIRED_VERSION+)"
    if command_exists python3; then
        log_verbose "Location: $(command -v python3)"
    elif command_exists python; then
        log_verbose "Location: $(command -v python)"
    fi
else
    log_warning "Python $PYTHON_VERSION found, but version $REQUIRED_VERSION+ is required."
    log_info "Attempting to install Python $REQUIRED_VERSION+..."
    
    # Try to install/upgrade Python automatically
    if install_python_with_fallbacks; then
        # Re-check after installation
        PYTHON_VERSION=$(get_python_version)
        if version_ge "$PYTHON_VERSION" "$REQUIRED_VERSION"; then
            log_success "Python $PYTHON_VERSION installed and verified (required: $REQUIRED_VERSION+)"
            if command_exists python3; then
                log_verbose "Location: $(command -v python3)"
            elif command_exists python; then
                log_verbose "Location: $(command -v python)"
            fi
        else
            log_error "Python upgrade succeeded but version check failed"
            exit 1
        fi
    else
        log_error "Python upgrade failed. Please upgrade manually."
        exit 1
    fi
fi

# Enhanced UV installation with multiple fallbacks
install_uv_with_fallbacks() {
    log_info "UV not found. Attempting automatic installation..."
    
    # Detect package manager
    local PACKAGE_MANAGER=""
    if command_exists brew; then
        PACKAGE_MANAGER="brew"
    elif command_exists apt; then
        PACKAGE_MANAGER="apt"
    elif command_exists dnf; then
        PACKAGE_MANAGER="dnf"
    elif command_exists yum; then
        PACKAGE_MANAGER="yum"
    fi
    
    # Method 1: Try Homebrew first (if available on macOS)
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        log_info "Trying: brew install uv"
        log_verbose "Using Homebrew package manager"
        if brew install uv >/dev/null 2>&1; then
            log_success "UV installed successfully via Homebrew"
            return 0
        else
            log_warning "Homebrew installation failed. Trying alternative methods..."
        fi
    fi
    
    # Method 2: Try curl installer
    if command_exists curl; then
        log_info "Trying: curl installer"
        log_verbose "Using official UV installer via curl"
        if curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; then
            # Add to PATH for current session
            export PATH="$HOME/.local/bin:$PATH"
            export PATH="$HOME/.cargo/bin:$PATH"
            if command_exists uv; then
                log_success "UV installed successfully via curl"
                return 0
            fi
        else
            log_warning "Curl installer failed. Trying wget..."
        fi
    else
        log_warning "curl not available. Trying wget..."
    fi
    
    # Method 3: Try wget installer (fallback for curl)
    if command_exists wget; then
        log_info "Trying: wget installer"
        log_verbose "Using official UV installer via wget"
        if wget -qO- https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; then
            # Add to PATH for current session
            export PATH="$HOME/.local/bin:$PATH"
            export PATH="$HOME/.cargo/bin:$PATH"
            if command_exists uv; then
                log_success "UV installed successfully via wget"
                return 0
            fi
        else
            log_warning "Wget installer failed. Trying pip..."
        fi
    else
        log_warning "wget not available. Trying pip..."
    fi
    
    # Method 4: Try pip install (if pip is available)
    if command_exists pip3 || command_exists pip; then
        local pip_cmd="pip3"
        if ! command_exists pip3; then
            pip_cmd="pip"
        fi
        
        log_info "Trying: $pip_cmd install --user uv"
        log_verbose "Installing UV via pip to user directory"
        if $pip_cmd install --user uv >/dev/null 2>&1; then
            # Add user bin to PATH
            if [[ "$OSTYPE" == "darwin"* ]]; then
                export PATH="$HOME/Library/Python/$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/bin:$PATH"
            else
                export PATH="$HOME/.local/bin:$PATH"
            fi
            
            if command_exists uv; then
                log_success "UV installed successfully via pip (user install)"
                return 0
            fi
        else
            log_warning "Pip installation failed."
        fi
    else
        log_warning "pip not available."
    fi
    
    # All methods failed
    log_error "All automatic installation methods failed."
    log_info "Please visit: https://docs.astral.sh/uv/getting-started/installation/"
    log_info "Manual installation options:"
    echo "  1. Download from GitHub: https://github.com/astral-sh/uv/releases"
    echo "  2. Use pipx: pipx install uv"
    echo "  3. Use cargo: cargo install --git https://github.com/astral-sh/uv uv"
    
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        echo "  4. Homebrew fallbacks:"
        echo "     - Xcode Command Line Tools: xcode-select --install"
        echo "     - Manual downloads: https://python.org, https://git-scm.com"
    fi
    
    return 1
}

# Step 2: Install uv if not present
log_step "Checking uv package manager..."
if ! command_exists uv; then
    # Try to install UV automatically
    if install_uv_with_fallbacks; then
        # Re-check after installation
        if command_exists uv; then
            UV_VERSION=$(uv --version 2>/dev/null | head -n1)
            log_success "UV Package Manager: $UV_VERSION (auto-installed)"
            log_verbose "Location: $(command -v uv)"
        fi
    else
        log_error "UV installation failed. Please install manually."
        exit 1
    fi
else
    UV_VERSION=$(uv --version 2>/dev/null | head -n1)
    log_success "UV Package Manager: $UV_VERSION"
    log_verbose "Location: $(command -v uv)"
fi



# Step 3: Check Git installation
log_step "Checking Git installation..."
if ! command_exists git; then
    log_info "Installing Git..."

    # Detect OS and install Git with fallbacks
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        log_verbose "Detected macOS system"
        if command_exists brew; then
            log_info "Trying: brew install git"
            log_verbose "Using Homebrew package manager"
            if brew install git >/dev/null 2>&1; then
                log_success "Git installed via Homebrew"
            else
                log_warning "Homebrew failed. Trying Xcode Command Line Tools..."
                log_info "Installing Xcode Command Line Tools (includes Git)"
                if xcode-select --install >/dev/null 2>&1; then
                    log_info "Xcode Command Line Tools installation initiated"
                    log_info "Please complete the installation in the popup dialog"
                    log_info "After installation, re-run this script"
                    exit 0
                else
                    log_error "Git installation failed. Manual options:"
                    echo "  1. Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                    echo "  2. Download Git: https://git-scm.com/download/mac"
                    echo "  3. Install Xcode Command Line Tools: xcode-select --install"
                    exit 1
                fi
            fi
        elif command_exists port; then
            log_info "Trying: MacPorts"
            log_verbose "Using MacPorts package manager"
            sudo port install git
        else
            log_warning "No package manager found. Trying Xcode Command Line Tools..."
            if xcode-select --install >/dev/null 2>&1; then
                log_info "Xcode Command Line Tools installation initiated"
                log_info "Please complete the installation and re-run this script"
                exit 0
            else
                log_error "Git installation failed. Please install manually:"
                echo "  1. Download from: https://git-scm.com/download/mac"
                echo "  2. Install Homebrew first, then: brew install git"
                exit 1
            fi
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        log_verbose "Detected Linux system"
        if command_exists apt; then
            log_info "Trying: apt install git"
            log_verbose "Using APT package manager"
            sudo apt update && sudo apt install -y git
        elif command_exists dnf; then
            log_info "Trying: dnf install git"
            log_verbose "Using DNF package manager"
            sudo dnf install -y git
        elif command_exists yum; then
            log_info "Trying: yum install git"
            log_verbose "Using YUM package manager"
            sudo yum install -y git
        elif command_exists pacman; then
            log_info "Trying: pacman -S git"
            log_verbose "Using Pacman package manager"
            sudo pacman -S git
        elif command_exists zypper; then
            log_info "Trying: zypper install git"
            log_verbose "Using Zypper package manager"
            sudo zypper install git
        else
            log_error "No supported package manager found. Please install Git manually:"
            echo "  1. Download from: https://git-scm.com/downloads"
            echo "  2. Use your distribution's package manager"
            exit 1
        fi
    else
        log_error "Unsupported operating system. Please install Git manually:"
        echo "  Download from: https://git-scm.com/downloads"
        exit 1
    fi

    # Verify Git installation
    if command_exists git; then
        GIT_VERSION=$(git --version)
        log_success "Git installed successfully: $GIT_VERSION"
        log_verbose "Location: $(command -v git)"
    else
        log_error "Git installation failed"
        exit 1
    fi
else
    GIT_VERSION=$(git --version)
    log_success "Git found: $GIT_VERSION"
    log_verbose "Location: $(command -v git)"
fi

# Function to run uv command with fallback paths
run_uv() {
    if command_exists uv; then
        uv "$@"
    elif [ -f "$HOME/.cargo/bin/uv" ]; then
        "$HOME/.cargo/bin/uv" "$@"
    elif [ -f "$HOME/.local/bin/uv" ]; then
        "$HOME/.local/bin/uv" "$@"
    else
        log_error "uv command not found. Please ensure uv is installed and in PATH"
        exit 1
    fi
}

# Step 3: Create virtual environment if it doesn't exist
log_step "Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    log_info "Creating virtual environment with uv..."
    run_uv venv
    if [ $? -eq 0 ]; then
        log_success "Virtual environment created"
    else
        log_error "Failed to create virtual environment"
        exit 1
    fi
else
    log_info "Virtual environment already exists"
fi

# Step 4: Activate virtual environment and install core ADK dependencies
log_step "Installing Google ADK and core dependencies..."
log_info "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies from pyproject.toml (includes google-adk and all dependencies)
log_info "Installing project dependencies..."
run_uv pip install -e .

if [ $? -eq 0 ]; then
    log_success "Core dependencies installed successfully"
else
    log_error "Failed to install dependencies"
    exit 1
fi

# Step 5: Verify installations
log_step "Verifying installations..."

# Check Google ADK
log_verbose "Checking Google ADK import..."
if python -c "import google.adk" 2>/dev/null; then
    ADK_VERSION=$(python -c "import google.adk; print(google.adk.__version__)" 2>/dev/null || echo "unknown")
    log_success "Google ADK $ADK_VERSION available"
    log_verbose "ADK location: $(python -c "import google.adk; print(google.adk.__file__)" 2>/dev/null)"
else
    log_error "Google ADK not found after installation"
    log_verbose "Try: uv pip install google-adk"
    exit 1
fi

# Check FastAPI
log_verbose "Checking FastAPI import..."
if python -c "import fastapi" 2>/dev/null; then
    FASTAPI_VERSION=$(python -c "import fastapi; print(fastapi.__version__)" 2>/dev/null || echo "unknown")
    log_success "FastAPI $FASTAPI_VERSION available for web interface"
    log_verbose "FastAPI location: $(python -c "import fastapi; print(fastapi.__file__)" 2>/dev/null)"
else
    log_error "FastAPI not found"
    log_verbose "Try: uv pip install fastapi"
    exit 1
fi

# Check httpx for MCP connections
log_verbose "Checking httpx import..."
if python -c "import httpx" 2>/dev/null; then
    HTTPX_VERSION=$(python -c "import httpx; print(httpx.__version__)" 2>/dev/null || echo "unknown")
    log_success "httpx $HTTPX_VERSION available for MCP connections"
    log_verbose "httpx location: $(python -c "import httpx; print(httpx.__file__)" 2>/dev/null)"
else
    log_error "httpx not found"
    log_verbose "Try: uv pip install httpx"
    exit 1
fi



echo ""
echo "==========================================================="
echo "🎉 Prerequisites Check Complete!"
echo "==========================================================="
echo ""
log_success "Python $PYTHON_VERSION"
log_success "UV package manager"
log_success "Git version control"
log_success "Virtual environment ready"
log_success "Google ADK installed"
log_success "Core dependencies installed"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Start AI Sidekick - run: uv run ai-sidekick --start"
echo "3. Access web interface at http://localhost:8087"
echo ""
