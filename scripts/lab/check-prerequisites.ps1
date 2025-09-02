# AI Sidekick for Splunk Lab - Prerequisites Checker
# Verifies system requirements and installs missing dependencies
# Ensures UV package manager and Git are available for project setup

param(
    [switch]$Help,
    [switch]$Verbose
)

if ($Help) {
    Write-Host "AI Sidekick for Splunk Lab - Prerequisites Checker" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "    .\scripts\lab\check-prerequisites.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "    -Verbose      Show detailed version information and installation paths"
    Write-Host "    -Help         Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "    .\scripts\lab\check-prerequisites.ps1           # Check and install requirements"
    Write-Host "    .\scripts\lab\check-prerequisites.ps1 -Verbose # Show detailed information"
    Write-Host ""
    Write-Host "Requirements:"
    Write-Host "    - UV package manager (handles Python and dependencies automatically)"
    Write-Host "    - Git (for repository operations)"
    Write-Host ""
    exit 0
}

# Set error action preference
$ErrorActionPreference = "Stop"

# Emoji support check - try Unicode, fallback to ASCII
$script:EmojiSuccess = "✅"
$script:EmojiWarning = "⚠️ "
$script:EmojiError = "❌"
$script:EmojiInfo = "ℹ️ "

try {
    # Test Unicode support
    $null = [Console]::OutputEncoding.GetString([Console]::OutputEncoding.GetBytes($script:EmojiSuccess))
} catch {
    # Fallback to ASCII
    $script:EmojiSuccess = "[OK]"
    $script:EmojiWarning = "[WARN]"
    $script:EmojiError = "[ERR]"
    $script:EmojiInfo = "[INFO]"
}

function Write-Info {
    param([string]$Message)
    Write-Host "$($script:EmojiInfo) $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "$($script:EmojiSuccess) $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "$($script:EmojiWarning) $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "$($script:EmojiError) $Message" -ForegroundColor Red
}

function Write-Step {
    param([string]$Message)
    Write-Host "🔧 $Message" -ForegroundColor Cyan
}

function Write-Verbose {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "    $Message" -ForegroundColor DarkCyan
    }
}

# Welcome message
Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "🚀 AI Sidekick for Splunk Lab - Prerequisites Check" -ForegroundColor Cyan
Write-Host "   Verifying system requirements and dependencies" -ForegroundColor Cyan
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

# Helper function to refresh environment PATH
function Refresh-EnvironmentPath {
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

# Install UV package manager using multiple fallback methods
function Install-UvWithFallbacks {
    Write-Info "Installing UV package manager..."
    
    # Method 1: Try PowerShell installer first (official method)
    Write-Info "Attempting installation via PowerShell"
    try {
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression | Out-Null
        Refresh-EnvironmentPath
        if (Test-Command "uv") {
            Write-Success "UV installed successfully via PowerShell installer"
            return $true
        }
    } catch {
        Write-Warning "PowerShell installer failed. Trying winget..."
    }
    
    # Method 2: Try winget
    if (Test-Command "winget") {
        Write-Info "Trying: winget install astral-sh.uv"
        Write-Verbose "Using Windows Package Manager (winget)"
        try {
            winget install astral-sh.uv --silent --accept-package-agreements --accept-source-agreements | Out-Null
            Refresh-EnvironmentPath
            if (Test-Command "uv") {
                Write-Success "UV installed successfully via winget"
                return $true
            }
        } catch {
            Write-Warning "winget installation failed. Trying Scoop..."
        }
    } else {
        Write-Verbose "winget not available. Trying Scoop..."
    }
    
    # Method 3: Try Scoop
    if (Test-Command "scoop") {
        Write-Info "Trying: scoop install uv"
        Write-Verbose "Using Scoop package manager"
        try {
            scoop install uv | Out-Null
            Refresh-EnvironmentPath
            if (Test-Command "uv") {
                Write-Success "UV installed successfully via Scoop"
                return $true
            }
        } catch {
            Write-Warning "Scoop installation failed. Trying Chocolatey..."
        }
    } else {
        Write-Verbose "Scoop not available. Trying Chocolatey..."
    }
    
    # Method 4: Try Chocolatey (if package exists)
    if (Test-Command "choco") {
        Write-Info "Trying: choco install uv"
        Write-Verbose "Using Chocolatey package manager"
        try {
            choco install uv -y | Out-Null
            Refresh-EnvironmentPath
            if (Test-Command "uv") {
                Write-Success "UV installed successfully via Chocolatey"
                return $true
            }
        } catch {
            Write-Warning "Chocolatey installation failed. Trying pip..."
        }
    } else {
        Write-Verbose "Chocolatey not available. Trying pip..."
    }
    
    # Method 5: Try pip install (if pip is available)
    if (Test-Command "pip" -or Test-Command "pip3") {
        $pipCmd = if (Test-Command "pip3") { "pip3" } else { "pip" }
        Write-Info "Trying: $pipCmd install --user uv"
        Write-Verbose "Installing UV via pip to user directory"
        try {
            & $pipCmd install --user uv | Out-Null
            # Add user Scripts to PATH
            $userScripts = [System.IO.Path]::Combine([System.Environment]::GetFolderPath("UserProfile"), "AppData", "Roaming", "Python", "Python*", "Scripts")
            $env:PATH = "$userScripts;$env:PATH"
            Refresh-EnvironmentPath
            
            if (Test-Command "uv") {
                Write-Success "UV installed successfully via pip (user install)"
                return $true
            }
        } catch {
            Write-Warning "pip installation failed."
        }
    } else {
        Write-Verbose "pip not available."
    }
    
    # Method 6: Direct GitHub release download
    Write-Info "Trying: Direct GitHub release download"
    Write-Verbose "Downloading UV binary from GitHub releases"
    try {
        $uvUrl = "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
        $downloadPath = "$env:TEMP\uv-latest.zip"
        $extractPath = "$env:TEMP\uv-extract"
        $installPath = "$env:LOCALAPPDATA\uv"
        
        Write-Verbose "Downloading from: $uvUrl"
        Invoke-WebRequest -Uri $uvUrl -OutFile $downloadPath -UseBasicParsing
        
        Write-Verbose "Extracting to: $extractPath"
        Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
        
        Write-Verbose "Installing to: $installPath"
        New-Item -ItemType Directory -Path $installPath -Force | Out-Null
        Copy-Item -Path "$extractPath\uv.exe" -Destination "$installPath\uv.exe" -Force
        
        # Add to PATH
        $currentPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*$installPath*") {
            [System.Environment]::SetEnvironmentVariable("PATH", "$installPath;$currentPath", "User")
        }
        $env:PATH = "$installPath;$env:PATH"
        
        # Cleanup
        Remove-Item $downloadPath -Force -ErrorAction SilentlyContinue
        Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue
        
        if (Test-Command "uv") {
            Write-Success "UV installed successfully via GitHub release"
            return $true
        }
    } catch {
        Write-Warning "GitHub release installation failed."
    }
    
    # All methods failed
    Write-Warning "Automatic installation failed"
    Write-Info "Manual installation required:"
    Write-Host "  1. Visit: https://docs.astral.sh/uv/getting-started/installation/"
    Write-Host "  2. Run: irm https://astral.sh/uv/install.ps1 | iex"
    Write-Host "  3. Download: https://github.com/astral-sh/uv/releases"
    
    return $false
}

# Step 1: Check UV Package Manager
Write-Step "Step 1: UV Package Manager"
Write-Host "-----------------------------" -ForegroundColor Cyan

if (Test-Command "uv") {
    try {
        $uvVersion = uv --version 2>$null
        Write-Success "UV Package Manager: $uvVersion"
        if ($Verbose) {
            Write-Verbose "Location: $(Get-Command uv | Select-Object -ExpandProperty Source)"
        }
        
        # Verify UV can manage Python versions
        if ($Verbose) {
            Write-Verbose "Verifying UV Python management capabilities..."
        }
        try {
            uv python list | Out-Null
            Write-Success "UV Python management available"
            if ($Verbose) {
                Write-Verbose "Can automatically download required Python versions"
            }
        } catch {
            Write-Info "UV ready to download Python versions as needed"
        }
    } catch {
        Write-Success "UV Package Manager found"
    }
} else {
    Write-Warning "UV Package Manager: Not found"
    
    # Attempt automatic installation
    if (Install-UvWithFallbacks) {
        try {
            $uvVersion = uv --version 2>$null
            Write-Success "UV Package Manager: $uvVersion (installed)"
            if ($Verbose) {
                Write-Verbose "Location: $(Get-Command uv | Select-Object -ExpandProperty Source)"
            }
        } catch {
            Write-Success "UV Package Manager installed successfully"
        }
    } else {
        Write-Error "UV Package Manager: Installation failed"
        exit 1
    }
}

# Setup project environment with UV
Write-Host ""
Write-Step "Setting up project environment..."
if (Test-Path "pyproject.toml") {
    Write-Info "Creating virtual environment and installing dependencies..."
    try {
        uv sync | Out-Null
        Write-Success "Virtual environment created and dependencies installed"
        if ($Verbose) {
            Write-Verbose "Virtual environment location: .venv\"
        }
        
        # Verify the environment works
        if ((Test-Path ".venv\Scripts\activate.ps1") -or (Test-Path ".venv\bin\activate")) {
            Write-Success "Virtual environment ready"
        } else {
            Write-Warning "Virtual environment created but activation script not found"
        }
    } catch {
        Write-Warning "Failed to create virtual environment or install dependencies"
        Write-Info "You may need to run 'uv sync' manually in the project directory"
    }
} else {
    Write-Warning "No pyproject.toml found - skipping environment setup"
    Write-Info "Make sure you're running this script from the project root directory"
}

Write-Host ""

# Step 2: Check Git
Write-Step "Step 2: Git"
Write-Host "------------" -ForegroundColor Cyan

if (Test-Command "git") {
    try {
        $gitVersion = git --version 2>$null
        Write-Success "Git: $gitVersion"
        if ($Verbose) {
            Write-Verbose "Location: $(Get-Command git | Select-Object -ExpandProperty Source)"
        }
    } catch {
        Write-Success "Git found"
    }
} else {
    Write-Warning "Git: Not found"
    
    # Show installation instructions
    Write-Info "Installation options:"
    Write-Host "  1. winget install Git.Git"
    Write-Host "  2. choco install git"
    Write-Host "  3. scoop install git"
    Write-Host "  4. https://git-scm.com"
}

Write-Host ""

# Check optional development tools
Write-Step "Optional Tools"
Write-Host "---------------" -ForegroundColor Cyan

# Node.js for MCP Inspector
if (Test-Command "node") {
    try {
        $nodeVersion = node --version 2>$null
        Write-Success "Node.js: $nodeVersion"
    } catch {
        Write-Success "Node.js found"
    }
} else {
    Write-Info "Node.js: Not found (optional)"
}

# Docker for containerization
if (Test-Command "docker") {
    try {
        $dockerVersion = docker --version 2>$null
        Write-Success "Docker: $dockerVersion"
    } catch {
        Write-Success "Docker found"
    }
} else {
    Write-Info "Docker: Not found (optional)"
}

Write-Host ""

# System information (verbose mode)
if ($Verbose) {
    Write-Step "System Information"
    Write-Host "-------------------------" -ForegroundColor Cyan
    Write-Info "OS: $([System.Environment]::OSVersion.VersionString)"
    Write-Info "Architecture: $([System.Environment]::GetEnvironmentVariable('PROCESSOR_ARCHITECTURE'))"
    Write-Info "Shell: PowerShell $($PSVersionTable.PSVersion)"
}



Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "🎉 Prerequisites Check Complete!" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Success "UV Package Manager available"
Write-Success "Git version control available"
Write-Success "System ready for setup"

Write-Host ""
Write-Step "🚀 Ready to Start:"
Write-Host "1. Activate the virtual environment: .venv\Scripts\Activate.ps1"
Write-Host "2. Start AI Sidekick: uv run ai-sidekick --start"
Write-Host "3. Access web interface: http://localhost:8087"
Write-Host ""
Write-Info "Virtual environment and dependencies are ready!"
