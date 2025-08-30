#!/bin/bash

# AI Sidekick for Splunk Lab - Prerequisites Installation Script (Unix/Linux/Mac)
# Checks and installs required packages for the Google ADK + MCP + Splunk setup

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${YELLOW}[STEP]${NC} $1"
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

# Step 1: Check Python
log_step "Checking Python installation..."
PYTHON_VERSION=$(get_python_version)
REQUIRED_VERSION="3.11"

if [[ "$PYTHON_VERSION" == "0.0" ]]; then
    log_error "Python not found. Please install Python 3.11 or higher."
    echo ""
    echo "Installation options:"
    echo "  macOS:   brew install python@3.11"
    echo "  Ubuntu:  sudo apt install python3.11 python3.11-venv"
    echo "  CentOS:  sudo yum install python3.11"
    echo ""
    exit 1
elif version_ge "$PYTHON_VERSION" "$REQUIRED_VERSION"; then
    log_success "Python $PYTHON_VERSION found (required: $REQUIRED_VERSION+)"
else
    log_error "Python $PYTHON_VERSION found, but version $REQUIRED_VERSION+ is required."
    exit 1
fi

# Step 2: Install uv if not present
log_step "Checking uv package manager..."
if ! command_exists uv; then
    log_info "Installing uv package manager..."

    # Install uv using the official installer
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        log_info "uv installer completed successfully"
    else
        log_error "Failed to download or run uv installer"
        exit 1
    fi

    # Add uv to PATH for current session - try multiple possible locations
    export PATH="$HOME/.cargo/bin:$PATH"
    export PATH="$HOME/.local/bin:$PATH"

    # Source shell profile to ensure PATH is updated
    if [ -f "$HOME/.bashrc" ]; then
        source "$HOME/.bashrc" 2>/dev/null || true
    fi
    if [ -f "$HOME/.zshrc" ]; then
        source "$HOME/.zshrc" 2>/dev/null || true
    fi

    # Wait a moment for the installation to complete
    sleep 2

    # Check if uv is now available
    if command_exists uv; then
        log_success "uv installed and available"
    elif [ -f "$HOME/.cargo/bin/uv" ]; then
        log_success "uv installed at $HOME/.cargo/bin/uv"
        log_info "Note: You may need to restart your terminal or run 'source ~/.bashrc' for uv to be available in new sessions"
    elif [ -f "$HOME/.local/bin/uv" ]; then
        log_success "uv installed at $HOME/.local/bin/uv"
        log_info "Note: You may need to restart your terminal or run 'source ~/.bashrc' for uv to be available in new sessions"
    else
        log_error "uv installation completed but uv command not found in PATH"
        log_info "Please manually add uv to your PATH or restart your terminal"
        log_info "Installation guide: https://docs.astral.sh/uv/"
        exit 1
    fi
else
    log_success "uv package manager found"
fi

# Step 2.5: Check Git installation
log_step "Checking Git installation..."
if ! command_exists git; then
    log_info "Installing Git..."

    # Detect OS and install Git
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install git
        elif command_exists port; then
            sudo port install git
        else
            log_error "Git not found. Please install Git:"
            echo "  Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "  Then run: brew install git"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt; then
            sudo apt update && sudo apt install -y git
        elif command_exists dnf; then
            sudo dnf install -y git
        elif command_exists yum; then
            sudo yum install -y git
        elif command_exists pacman; then
            sudo pacman -S git
        elif command_exists zypper; then
            sudo zypper install git
        else
            log_error "Git not found. Please install Git using your system's package manager"
            exit 1
        fi
    else
        log_error "Git not found. Please install Git for your operating system"
        exit 1
    fi

    # Verify Git installation
    if command_exists git; then
        log_success "Git installed successfully"
    else
        log_error "Git installation failed"
        exit 1
    fi
else
    log_success "Git found: $(git --version)"
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
if python -c "import google.adk" 2>/dev/null; then
    ADK_VERSION=$(python -c "import google.adk; print(google.adk.__version__)" 2>/dev/null || echo "unknown")
    log_success "Google ADK $ADK_VERSION available"
else
    log_error "Google ADK not found after installation"
    exit 1
fi

# Check FastAPI
if python -c "import fastapi" 2>/dev/null; then
    log_success "FastAPI available for web interface"
else
    log_error "FastAPI not found"
    exit 1
fi

# Check httpx for MCP connections
if python -c "import httpx" 2>/dev/null; then
    log_success "httpx available for MCP connections"
else
    log_error "httpx not found"
    exit 1
fi



echo ""
echo "==========================================================="
echo "🎉 Prerequisites Check Complete!"
echo "==========================================================="
echo ""
log_success "✅ Python $PYTHON_VERSION"
log_success "✅ uv package manager"
log_success "✅ Git version control"
log_success "✅ Virtual environment ready"
log_success "✅ Google ADK installed"
log_success "✅ Core dependencies installed"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Start AI Sidekick - run: uv run start-lab"
echo ""
