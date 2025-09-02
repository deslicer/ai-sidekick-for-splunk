#!/bin/bash

# AI Sidekick for Splunk Lab - Prerequisites Checker
# Verifies system requirements and installs missing dependencies
# Ensures UV package manager and Git are available for project setup

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
AI Sidekick for Splunk Lab - Prerequisites Checker

Usage:
    ./scripts/lab/check-prerequisites.sh [options]

Options:
    --verbose, -v     Show detailed version information and installation paths
    --help, -h        Show this help message

Examples:
    ./scripts/lab/check-prerequisites.sh           # Check and install requirements
    ./scripts/lab/check-prerequisites.sh --verbose # Show detailed information

Requirements:
    - UV package manager (handles Python and dependencies automatically)
    - Git (for repository operations)
EOF
    exit 0
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emoji support check
if command -v locale >/dev/null 2>&1 && [[ "$(locale charmap 2>/dev/null)" == "UTF-8" ]]; then
    EMOJI_SUCCESS="✅"
    EMOJI_WARNING="⚠️ "
    EMOJI_ERROR="❌"
    EMOJI_INFO="ℹ️ "
    EMOJI_TOOLS="🔧"
    EMOJI_PARTY="🎉"
else
    EMOJI_SUCCESS="[OK]"
    EMOJI_WARNING="[WARN]"
    EMOJI_ERROR="[ERR]"
    EMOJI_INFO="[INFO]"
    EMOJI_TOOLS="[TOOLS]"
    EMOJI_PARTY="[DONE]"
fi

# Output functions
log_success() {
    echo -e "${GREEN}${EMOJI_SUCCESS} $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}${EMOJI_WARNING} $1${NC}"
}

log_error() {
    echo -e "${RED}${EMOJI_ERROR} $1${NC}"
}

log_info() {
    echo -e "${BLUE}${EMOJI_INFO} $1${NC}"
}

log_step() {
    echo -e "${CYAN}${EMOJI_TOOLS} $1${NC}"
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}${EMOJI_INFO} $1${NC}"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Track missing requirements
missing_requirements=()

# Welcome message
echo ""
echo "==========================================================="
echo "🚀 AI Sidekick for Splunk Lab - Prerequisites Check"
echo "   Verifying system requirements and dependencies"
echo "==========================================================="
echo ""

# Install UV package manager using multiple fallback methods
install_uv_with_fallbacks() {
    log_info "UV not found. Installing UV package manager..."
    
    # Method 1: Try curl installer (most reliable)
    if command_exists curl; then
        log_info "Attempting installation via curl"
        if curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; then
            # Add to PATH for current session
            export PATH="$HOME/.local/bin:$PATH"
            if command_exists uv; then
                log_success "UV installed successfully via curl"
                return 0
            fi
        else
            log_warning "Curl installation failed, trying wget"
        fi
    else
        log_warning "curl not available, trying wget"
    fi
    
    # Method 2: Try wget installer (fallback for curl)
    if command_exists wget; then
        log_info "Attempting installation via wget"
        if wget -qO- https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; then
            # Add to PATH for current session
            export PATH="$HOME/.local/bin:$PATH"
            if command_exists uv; then
                log_success "UV installed successfully via wget"
                return 0
            fi
        else
            log_warning "wget installation failed, trying Homebrew"
        fi
    else
        log_warning "wget not available, trying Homebrew"
    fi
    
    # Method 3: Try Homebrew (if available)
    if command_exists brew; then
        log_info "Attempting installation via Homebrew"
        if brew install uv >/dev/null 2>&1; then
            if command_exists uv; then
                log_success "UV installed successfully via Homebrew"
                return 0
            fi
        else
            log_warning "Homebrew installation failed, trying pip"
        fi
    else
        log_info "Homebrew not available, trying pip"
    fi
    
    # Method 4: Try pip install (if any Python is available)
    if command_exists pip3 || command_exists pip || command_exists python3 || command_exists python; then
        local pip_cmd=""
        if command_exists pip3; then
            pip_cmd="pip3"
        elif command_exists pip; then
            pip_cmd="pip"
        elif command_exists python3; then
            pip_cmd="python3 -m pip"
        elif command_exists python; then
            pip_cmd="python -m pip"
        fi
        
        if [[ -n "$pip_cmd" ]]; then
            log_info "Attempting installation via pip"
            if $pip_cmd install --user uv >/dev/null 2>&1; then
                # Add user bin to PATH
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    # macOS
                    if command_exists python3; then
                        export PATH="$HOME/Library/Python/$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/bin:$PATH"
                    fi
                else
                    # Linux
                    export PATH="$HOME/.local/bin:$PATH"
                fi
                
                if command_exists uv; then
                    log_success "UV installed successfully via pip (user install)"
                    return 0
                fi
            else
                log_warning "pip installation failed"
            fi
        fi
    fi
    
    # All methods failed
    log_error "Automatic installation failed"
    log_info "Manual installation required:"
    echo "  1. Visit: https://docs.astral.sh/uv/getting-started/installation/"
    echo "  2. Run: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  3. Download: https://github.com/astral-sh/uv/releases"
    return 1
}

# Check UV package manager availability
log_step "Step 1: UV Package Manager"
echo "-----------------------------"

if command_exists uv; then
    UV_VERSION=$(uv --version 2>/dev/null | head -n1)
    log_success "UV Package Manager: $UV_VERSION"
    log_verbose "Location: $(command -v uv)"
    
    # Verify UV can manage Python versions
    log_verbose "Verifying UV Python management capabilities..."
    if uv python list >/dev/null 2>&1; then
        log_success "UV Python management available"
        log_verbose "Can automatically download required Python versions"
    else
        log_info "UV ready to download Python versions as needed"
    fi
else
    log_warning "UV Package Manager: Not found"
    
    # Attempt automatic installation
    if install_uv_with_fallbacks; then
        UV_VERSION=$(uv --version 2>/dev/null | head -n1)
        log_success "UV Package Manager: $UV_VERSION (installed)"
        log_verbose "Location: $(command -v uv)"
    else
        log_error "UV Package Manager: Installation failed"
        missing_requirements+=("UV Package Manager")
        exit 1
    fi
fi

# Setup project environment with UV
echo ""
log_step "Setting up project environment..."
if [[ -f "pyproject.toml" ]]; then
    log_info "Creating virtual environment and installing dependencies..."
    if uv sync >/dev/null 2>&1; then
        log_success "Virtual environment created and dependencies installed"
        log_verbose "Virtual environment location: .venv/"
        
        # Verify the environment works
        if [[ -f ".venv/bin/activate" ]] || [[ -f ".venv/Scripts/activate" ]]; then
            log_success "Virtual environment ready"
        else
            log_warning "Virtual environment created but activation script not found"
        fi
    else
        log_error "Failed to create virtual environment or install dependencies"
        log_info "You may need to run 'uv sync' manually in the project directory"
    fi
else
    log_warning "No pyproject.toml found - skipping environment setup"
    log_info "Make sure you're running this script from the project root directory"
fi

echo ""

# Check Git version control system
log_step "Step 2: Git"
echo "------------"

if command_exists git; then
    GIT_VERSION=$(git --version 2>/dev/null | head -n1)
    log_success "Git: $GIT_VERSION"
    log_verbose "Location: $(command -v git)"
else
    log_error "Git: Not found"
    missing_requirements+=("Git")
    
    # Show installation instructions
    if [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "Installation options:"
        echo "  1. brew install git"
        echo "  2. xcode-select --install"
        echo "  3. https://git-scm.com"
    elif command -v apt >/dev/null 2>&1; then
        log_info "Install: sudo apt install git"
    elif command -v dnf >/dev/null 2>&1; then
        log_info "Install: sudo dnf install git"
    elif command -v yum >/dev/null 2>&1; then
        log_info "Install: sudo yum install git"
    else
        log_info "Download: https://git-scm.com"
    fi
fi

echo ""

# Check optional development tools
log_step "Optional Tools"
echo "---------------"

# Node.js for MCP Inspector
if command_exists node; then
    NODE_VERSION=$(node --version 2>/dev/null | head -n1)
    log_success "Node.js: $NODE_VERSION"
else
    log_info "Node.js: Not found (optional)"
fi

# Docker for containerization
if command_exists docker; then
    DOCKER_VERSION=$(docker --version 2>/dev/null | head -n1)
    log_success "Docker: $DOCKER_VERSION"
else
    log_info "Docker: Not found (optional)"
fi

echo ""

# System information (verbose mode)
if [[ "$VERBOSE" == "true" ]]; then
    log_step "System Information"
    echo "-------------------------"
    
    # Operating System
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        log_info "OS: $PRETTY_NAME"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        macos_version=$(sw_vers -productVersion 2>/dev/null || echo "Unknown")
        log_info "OS: macOS $macos_version"
    else
        log_info "OS: $(uname -s) $(uname -r)"
    fi
    
    # Architecture
    log_info "Architecture: $(uname -m)"
    
    # Shell
    log_info "Shell: $SHELL"
    
    echo ""
fi

# Final summary
echo "================================================================"
log_step "${EMOJI_PARTY} Prerequisites Check Complete!"
echo "================================================================"
echo ""

if [[ ${#missing_requirements[@]} -eq 0 ]]; then
    # Success summary
    log_success "UV Package Manager available"
    log_success "Git version control available"
    log_success "System ready for setup"
    
    echo ""
    log_step "🚀 Ready to Start:"
    echo "1. Activate the virtual environment: source .venv/bin/activate"
    echo "2. Start AI Sidekick: uv run ai-sidekick --start"
    echo "3. Access web interface: http://localhost:8087"
    echo ""
    log_info "Virtual environment and dependencies are ready!"
else
    log_error "Missing required tools: $(IFS=', '; echo "${missing_requirements[*]}")"
    echo ""
    log_step "Please install the missing tools and re-run this script."
fi

# Exit with appropriate code
if [[ ${#missing_requirements[@]} -gt 0 ]]; then
    exit 1
else
    exit 0
fi
