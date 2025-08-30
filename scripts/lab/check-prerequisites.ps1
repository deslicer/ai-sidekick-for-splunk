# AI Sidekick for Splunk Lab - Prerequisites Installation Script (Windows PowerShell)
# Checks and installs required packages for Google ADK + MCP + Splunk setup

param(
    [switch]$Help
)

if ($Help) {
    Write-Host "AI Sidekick for Splunk Lab - Prerequisites Check" -ForegroundColor Cyan
    Write-Host "Google ADK + MCP + Splunk Setup"
    Write-Host ""
    Write-Host "Usage: .\check-prerequisites.ps1"
    Write-Host ""
    exit 0
}

# Set error action preference
$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] $Message" -ForegroundColor Magenta
}

# Welcome message
Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "🚀 AI Sidekick for Splunk Lab - Prerequisites Check" -ForegroundColor Cyan
Write-Host "   Google ADK + MCP + Splunk Setup" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to get Python version
function Get-PythonVersion {
    try {
        if (Test-Command "python") {
            $version = python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>$null
            return $version
        } elseif (Test-Command "python3") {
            $version = python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>$null
            return $version
        } else {
            return "0.0"
        }
    } catch {
        return "0.0"
    }
}

# Function to compare versions
function Compare-Version {
    param([string]$Current, [string]$Required)
    try {
        $currentParts = $Current.Split('.')
        $requiredParts = $Required.Split('.')

        for ($i = 0; $i -lt [Math]::Max($currentParts.Length, $requiredParts.Length); $i++) {
            $currentPart = if ($i -lt $currentParts.Length) { [int]$currentParts[$i] } else { 0 }
            $requiredPart = if ($i -lt $requiredParts.Length) { [int]$requiredParts[$i] } else { 0 }

            if ($currentPart -gt $requiredPart) { return $true }
            if ($currentPart -lt $requiredPart) { return $false }
        }
        return $true
    } catch {
        return $false
    }
}

# Step 1: Check Python
Write-Step "Checking Python installation..."
$pythonVersion = Get-PythonVersion
$requiredVersion = "3.11"

if ($pythonVersion -eq "0.0") {
    Write-Error "Python not found. Please install Python 3.11 or higher."
    Write-Host ""
    Write-Host "Installation options:"
    Write-Host "  Download from: https://python.org"
    Write-Host "  Windows Store: python3"
    Write-Host "  Chocolatey: choco install python311"
    Write-Host ""
    exit 1
} elseif (Compare-Version $pythonVersion $requiredVersion) {
    Write-Success "Python $pythonVersion found (required: $requiredVersion+)"
} else {
    Write-Error "Python $pythonVersion found, but version $requiredVersion+ is required."
    exit 1
}

# Step 2: Install uv if not present
Write-Step "Checking uv package manager..."
if (-not (Test-Command "uv")) {
    Write-Info "Installing uv package manager..."
    try {
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        # Refresh PATH for current session
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

        if (Test-Command "uv") {
            Write-Success "uv installed successfully"
        } else {
            Write-Error "Failed to install uv. Please install manually: https://docs.astral.sh/uv/"
            exit 1
        }
    } catch {
        Write-Error "Failed to install uv: $($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Success "uv package manager found"
}

# Step 2.5: Check Git installation
Write-Step "Checking Git installation..."
if (-not (Test-Command "git")) {
    Write-Info "Installing Git..."
    try {
        # Try winget first (Windows 10 1709+ and Windows 11)
        if (Test-Command "winget") {
            winget install Git.Git --silent --accept-package-agreements --accept-source-agreements
        }
        # Try chocolatey as fallback
        elseif (Test-Command "choco") {
            choco install git -y
        }
        else {
            Write-Error "Git not found. Please install Git:"
            Write-Host "  Option 1: Download from https://git-scm.com/download/win"
            Write-Host "  Option 2: Install winget: winget install Git.Git"
            Write-Host "  Option 3: Install chocolatey: choco install git"
            exit 1
        }

        # Refresh PATH for current session
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

        # Verify Git installation
        if (Test-Command "git") {
            Write-Success "Git installed successfully"
        } else {
            Write-Error "Git installation failed. Please install Git manually from https://git-scm.com/download/win"
            exit 1
        }
    } catch {
        Write-Error "Failed to install Git: $($_.Exception.Message)"
        Write-Host "Please install Git manually from https://git-scm.com/download/win"
        exit 1
    }
} else {
    $gitVersion = git --version 2>$null
    Write-Success "Git found: $gitVersion"
}

# Step 3: Create virtual environment if it doesn't exist
Write-Step "Setting up Python virtual environment..."
if (-not (Test-Path ".venv")) {
    Write-Info "Creating virtual environment with uv..."
    try {
        uv venv
        Write-Success "Virtual environment created"
    } catch {
        Write-Error "Failed to create virtual environment: $($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Info "Virtual environment already exists"
}

# Step 4: Install core ADK dependencies
Write-Step "Installing Google ADK and core dependencies..."
Write-Info "Activating virtual environment..."
& ".venv\Scripts\Activate.ps1"

# Install dependencies from pyproject.toml (includes google-adk and all dependencies)
Write-Info "Installing project dependencies..."
uv pip install -e .

Write-Success "Core dependencies installed successfully"

# Step 5: Verify installations
Write-Step "Verifying installations..."

# Check Google ADK
try {
    $adkTest = python -c "import google.adk; print('OK')" 2>$null
    if ($adkTest -eq "OK") {
        try {
            $adkVersion = python -c "import google.adk; print(google.adk.__version__)" 2>$null
            Write-Success "Google ADK $adkVersion available"
        } catch {
            Write-Success "Google ADK available"
        }
    } else {
        Write-Error "Google ADK not found after installation"
        exit 1
    }
} catch {
    Write-Error "Google ADK not found after installation"
    exit 1
}

# Check FastAPI
try {
    $fastapiTest = python -c "import fastapi; print('OK')" 2>$null
    if ($fastapiTest -eq "OK") {
        Write-Success "FastAPI available for web interface"
    } else {
        Write-Error "FastAPI not found"
        exit 1
    }
} catch {
    Write-Error "FastAPI not found"
    exit 1
}

# Check httpx for MCP connections
try {
    $httpxTest = python -c "import httpx; print('OK')" 2>$null
    if ($httpxTest -eq "OK") {
        Write-Success "httpx available for MCP connections"
    } else {
        Write-Error "httpx not found"
        exit 1
    }
} catch {
    Write-Error "httpx not found"
    exit 1
}



Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "🎉 Prerequisites Check Complete!" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Success "✅ Python $pythonVersion"
Write-Success "✅ uv package manager"
Write-Success "✅ Git version control"
Write-Success "✅ Virtual environment ready"
Write-Success "✅ Google ADK installed"
Write-Success "✅ Core dependencies installed"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Activate the virtual environment: .venv\Scripts\Activate.ps1"
Write-Host "2. Start AI Sidekick - run: uv run start-lab"
Write-Host ""
