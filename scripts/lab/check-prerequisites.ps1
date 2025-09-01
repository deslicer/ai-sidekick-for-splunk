# AI Sidekick for Splunk Lab - Prerequisites Installation Script (Windows PowerShell)
# Checks and installs required packages for Google ADK + MCP + Splunk setup

param(
    [switch]$Help,
    [switch]$Verbose
)

if ($Help) {
    Write-Host "AI Sidekick for Splunk Lab - Prerequisites Installation Script (Windows PowerShell)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "    .\scripts\lab\check-prerequisites.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "    -Verbose      Show detailed version information and installation paths"
    Write-Host "    -Help         Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "    .\scripts\lab\check-prerequisites.ps1           # Basic check and install"
    Write-Host "    .\scripts\lab\check-prerequisites.ps1 -Verbose # Detailed information"
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

# Enhanced Python installation with multiple fallbacks
function Install-PythonWithFallbacks {
    Write-Info "Python 3.11+ not found. Attempting automatic installation..."
    
    # Method 1: Try winget first (Windows 10 1709+ and Windows 11)
    if (Test-Command "winget") {
        Write-Info "Trying: winget install Python.Python.3.11"
        Write-Verbose "Using Windows Package Manager (winget)"
        try {
            winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements | Out-Null
            Refresh-EnvironmentPath
            if (Test-Command "python" -or Test-Command "python3") {
                Write-Success "Python 3.11 installed successfully via winget"
                return $true
            }
        } catch {
            Write-Warning "winget installation failed. Trying Chocolatey..."
        }
    } else {
        Write-Verbose "winget not available. Trying Chocolatey..."
    }
    
    # Method 2: Try Chocolatey
    if (Test-Command "choco") {
        Write-Info "Trying: choco install python311"
        Write-Verbose "Using Chocolatey package manager"
        try {
            choco install python311 -y | Out-Null
            Refresh-EnvironmentPath
            if (Test-Command "python" -or Test-Command "python3") {
                Write-Success "Python 3.11 installed successfully via Chocolatey"
                return $true
            }
        } catch {
            Write-Warning "Chocolatey installation failed. Trying Scoop..."
        }
    } else {
        Write-Verbose "Chocolatey not available. Trying Scoop..."
    }
    
    # Method 3: Try Scoop
    if (Test-Command "scoop") {
        Write-Info "Trying: scoop install python311"
        Write-Verbose "Using Scoop package manager"
        try {
            scoop install python | Out-Null
            Refresh-EnvironmentPath
            if (Test-Command "python" -or Test-Command "python3") {
                Write-Success "Python installed successfully via Scoop"
                return $true
            }
        } catch {
            Write-Warning "Scoop installation failed. Trying direct download..."
        }
    } else {
        Write-Verbose "Scoop not available. Trying direct download..."
    }
    
    # Method 4: Direct download and install
    Write-Info "Trying: Direct download from python.org"
    Write-Verbose "Downloading Python installer directly"
    try {
        $pythonUrl = "https://www.python.org/ftp/python/3.11.10/python-3.11.10-amd64.exe"
        $installerPath = "$env:TEMP\python-3.11.10-installer.exe"
        
        Write-Verbose "Downloading from: $pythonUrl"
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
        
        Write-Verbose "Running silent installation..."
        Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" -Wait
        
        Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
        Refresh-EnvironmentPath
        
        if (Test-Command "python" -or Test-Command "python3") {
            Write-Success "Python 3.11 installed successfully via direct download"
            return $true
        }
    } catch {
        Write-Warning "Direct download installation failed."
    }
    
    # All methods failed
    Write-Error "All automatic Python installation methods failed."
    Write-Info "Please install Python 3.11+ manually:"
    Write-Host "  Windows Options:"
    Write-Host "  1. Official installer: https://www.python.org/downloads/"
    Write-Host "  2. Microsoft Store: ms-windows-store://pdp/?productid=9NRWMJP3717K"
    Write-Host "  3. winget: winget install Python.Python.3.11"
    Write-Host "  4. Chocolatey: choco install python311"
    Write-Host "  5. Scoop: scoop install python"
    
    return $false
}

# Helper function to refresh environment PATH
function Refresh-EnvironmentPath {
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

# Step 1: Check Python
Write-Step "Checking Python installation..."
$pythonVersion = Get-PythonVersion
$requiredVersion = "3.11"

if ($pythonVersion -eq "0.0") {
    # Try to install Python automatically
    if (Install-PythonWithFallbacks) {
        # Re-check after installation
        $pythonVersion = Get-PythonVersion
        if (Compare-Version $pythonVersion $requiredVersion) {
            Write-Success "Python $pythonVersion installed and verified (required: $requiredVersion+)"
            if (Test-Command "python") {
                Write-Verbose "Location: $(Get-Command python | Select-Object -ExpandProperty Source)"
            } elseif (Test-Command "python3") {
                Write-Verbose "Location: $(Get-Command python3 | Select-Object -ExpandProperty Source)"
            }
        } else {
            Write-Error "Python installation succeeded but version check failed"
            exit 1
        }
    } else {
        Write-Error "Python installation failed. Please install manually."
        exit 1
    }
} elseif (Compare-Version $pythonVersion $requiredVersion) {
    Write-Success "Python $pythonVersion found (required: $requiredVersion+)"
    if (Test-Command "python") {
        Write-Verbose "Location: $(Get-Command python | Select-Object -ExpandProperty Source)"
    } elseif (Test-Command "python3") {
        Write-Verbose "Location: $(Get-Command python3 | Select-Object -ExpandProperty Source)"
    }
} else {
    Write-Warning "Python $pythonVersion found, but version $requiredVersion+ is required."
    Write-Info "Attempting to install Python $requiredVersion+..."
    
    # Try to install/upgrade Python automatically
    if (Install-PythonWithFallbacks) {
        # Re-check after installation
        $pythonVersion = Get-PythonVersion
        if (Compare-Version $pythonVersion $requiredVersion) {
            Write-Success "Python $pythonVersion installed and verified (required: $requiredVersion+)"
            if (Test-Command "python") {
                Write-Verbose "Location: $(Get-Command python | Select-Object -ExpandProperty Source)"
            } elseif (Test-Command "python3") {
                Write-Verbose "Location: $(Get-Command python3 | Select-Object -ExpandProperty Source)"
            }
        } else {
            Write-Error "Python upgrade succeeded but version check failed"
            exit 1
        }
    } else {
        Write-Error "Python upgrade failed. Please upgrade manually."
        exit 1
    }
}

# Enhanced UV installation with multiple fallbacks
function Install-UvWithFallbacks {
    Write-Info "UV not found. Attempting automatic installation..."
    
    # Method 1: Try PowerShell installer first (official method)
    Write-Info "Trying: PowerShell installer"
    Write-Verbose "Using official UV installer via PowerShell"
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
    Write-Error "All automatic UV installation methods failed."
    Write-Info "Please install UV manually:"
    Write-Host "  Windows Options:"
    Write-Host "  1. PowerShell: irm https://astral.sh/uv/install.ps1 | iex"
    Write-Host "  2. winget: winget install astral-sh.uv"
    Write-Host "  3. Scoop: scoop install uv"
    Write-Host "  4. pip: pip install --user uv"
    Write-Host "  5. GitHub: https://github.com/astral-sh/uv/releases"
    Write-Host "  6. Documentation: https://docs.astral.sh/uv/getting-started/installation/"
    
    return $false
}

# Step 2: Install uv if not present
Write-Step "Checking uv package manager..."
if (-not (Test-Command "uv")) {
    # Try to install UV automatically
    if (Install-UvWithFallbacks) {
        # Re-check after installation
        if (Test-Command "uv") {
            try {
                $uvVersion = uv --version 2>$null
                Write-Success "UV Package Manager: $uvVersion (auto-installed)"
                Write-Verbose "Location: $(Get-Command uv | Select-Object -ExpandProperty Source)"
            } catch {
                Write-Success "UV Package Manager installed successfully"
            }
        }
    } else {
        Write-Error "UV installation failed. Please install manually."
        exit 1
    }
} else {
    try {
        $uvVersion = uv --version 2>$null
        Write-Success "UV Package Manager: $uvVersion"
        Write-Verbose "Location: $(Get-Command uv | Select-Object -ExpandProperty Source)"
    } catch {
        Write-Success "UV Package Manager found"
    }
}

# Enhanced Git installation with multiple fallbacks
function Install-GitWithFallbacks {
    Write-Info "Git not found. Attempting automatic installation..."
    
    # Method 1: Try winget first (Windows 10 1709+ and Windows 11)
    if (Test-Command "winget") {
        Write-Info "Trying: winget install Git.Git"
        Write-Verbose "Using Windows Package Manager (winget)"
        try {
            winget install Git.Git --silent --accept-package-agreements --accept-source-agreements | Out-Null
            Refresh-EnvironmentPath
            if (Test-Command "git") {
                Write-Success "Git installed successfully via winget"
                return $true
            }
        } catch {
            Write-Warning "winget installation failed. Trying Chocolatey..."
        }
    } else {
        Write-Verbose "winget not available. Trying Chocolatey..."
    }
    
    # Method 2: Try Chocolatey
    if (Test-Command "choco") {
        Write-Info "Trying: choco install git"
        Write-Verbose "Using Chocolatey package manager"
        try {
            choco install git -y | Out-Null
            Refresh-EnvironmentPath
            if (Test-Command "git") {
                Write-Success "Git installed successfully via Chocolatey"
                return $true
            }
        } catch {
            Write-Warning "Chocolatey installation failed. Trying Scoop..."
        }
    } else {
        Write-Verbose "Chocolatey not available. Trying Scoop..."
    }
    
    # Method 3: Try Scoop
    if (Test-Command "scoop") {
        Write-Info "Trying: scoop install git"
        Write-Verbose "Using Scoop package manager"
        try {
            scoop install git | Out-Null
            Refresh-EnvironmentPath
            if (Test-Command "git") {
                Write-Success "Git installed successfully via Scoop"
                return $true
            }
        } catch {
            Write-Warning "Scoop installation failed. Trying direct download..."
        }
    } else {
        Write-Verbose "Scoop not available. Trying direct download..."
    }
    
    # Method 4: Direct download and install
    Write-Info "Trying: Direct download from git-scm.com"
    Write-Verbose "Downloading Git installer directly"
    try {
        # Get the latest Git version download URL
        $gitUrl = "https://github.com/git-for-windows/git/releases/latest/download/Git-2.47.1-64-bit.exe"
        $installerPath = "$env:TEMP\git-installer.exe"
        
        Write-Verbose "Downloading from: $gitUrl"
        Invoke-WebRequest -Uri $gitUrl -OutFile $installerPath -UseBasicParsing
        
        Write-Verbose "Running silent installation..."
        Start-Process -FilePath $installerPath -ArgumentList "/SILENT", "/COMPONENTS=icons,ext\reg\shellhere,assoc,assoc_sh" -Wait
        
        Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
        Refresh-EnvironmentPath
        
        if (Test-Command "git") {
            Write-Success "Git installed successfully via direct download"
            return $true
        }
    } catch {
        Write-Warning "Direct download installation failed."
    }
    
    # All methods failed
    Write-Error "All automatic Git installation methods failed."
    Write-Info "Please install Git manually:"
    Write-Host "  Windows Options:"
    Write-Host "  1. Official installer: https://git-scm.com/download/win"
    Write-Host "  2. winget: winget install Git.Git"
    Write-Host "  3. Chocolatey: choco install git"
    Write-Host "  4. Scoop: scoop install git"
    Write-Host "  5. GitHub Desktop: https://desktop.github.com/ (includes Git)"
    
    return $false
}

# Step 3: Check Git installation
Write-Step "Checking Git installation..."
if (-not (Test-Command "git")) {
    # Try to install Git automatically
    if (Install-GitWithFallbacks) {
        # Re-check after installation
        if (Test-Command "git") {
            try {
                $gitVersion = git --version 2>$null
                Write-Success "Git installed successfully: $gitVersion"
                Write-Verbose "Location: $(Get-Command git | Select-Object -ExpandProperty Source)"
            } catch {
                Write-Success "Git installed successfully"
            }
        }
    } else {
        Write-Error "Git installation failed. Please install manually."
        exit 1
    }
} else {
    try {
        $gitVersion = git --version 2>$null
        Write-Success "Git found: $gitVersion"
        Write-Verbose "Location: $(Get-Command git | Select-Object -ExpandProperty Source)"
    } catch {
        Write-Success "Git found"
    }
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
Write-Verbose "Checking Google ADK import..."
try {
    $adkTest = python -c "import google.adk; print('OK')" 2>$null
    if ($adkTest -eq "OK") {
        try {
            $adkVersion = python -c "import google.adk; print(google.adk.__version__)" 2>$null
            Write-Success "Google ADK $adkVersion available"
            Write-Verbose "ADK location: $(python -c "import google.adk; print(google.adk.__file__)" 2>$null)"
        } catch {
            Write-Success "Google ADK available"
        }
    } else {
        Write-Error "Google ADK not found after installation"
        Write-Verbose "Try: uv pip install google-adk"
        exit 1
    }
} catch {
    Write-Error "Google ADK not found after installation"
    Write-Verbose "Try: uv pip install google-adk"
    exit 1
}

# Check FastAPI
Write-Verbose "Checking FastAPI import..."
try {
    $fastapiTest = python -c "import fastapi; print('OK')" 2>$null
    if ($fastapiTest -eq "OK") {
        try {
            $fastapiVersion = python -c "import fastapi; print(fastapi.__version__)" 2>$null
            Write-Success "FastAPI $fastapiVersion available for web interface"
            Write-Verbose "FastAPI location: $(python -c "import fastapi; print(fastapi.__file__)" 2>$null)"
        } catch {
            Write-Success "FastAPI available for web interface"
        }
    } else {
        Write-Error "FastAPI not found"
        Write-Verbose "Try: uv pip install fastapi"
        exit 1
    }
} catch {
    Write-Error "FastAPI not found"
    Write-Verbose "Try: uv pip install fastapi"
    exit 1
}

# Check httpx for MCP connections
Write-Verbose "Checking httpx import..."
try {
    $httpxTest = python -c "import httpx; print('OK')" 2>$null
    if ($httpxTest -eq "OK") {
        try {
            $httpxVersion = python -c "import httpx; print(httpx.__version__)" 2>$null
            Write-Success "httpx $httpxVersion available for MCP connections"
            Write-Verbose "httpx location: $(python -c "import httpx; print(httpx.__file__)" 2>$null)"
        } catch {
            Write-Success "httpx available for MCP connections"
        }
    } else {
        Write-Error "httpx not found"
        Write-Verbose "Try: uv pip install httpx"
        exit 1
    }
} catch {
    Write-Error "httpx not found"
    Write-Verbose "Try: uv pip install httpx"
    exit 1
}



Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "🎉 Prerequisites Check Complete!" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Success "Python $pythonVersion"
Write-Success "UV package manager"
Write-Success "Git version control"
Write-Success "Virtual environment ready"
Write-Success "Google ADK installed"
Write-Success "Core dependencies installed"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Activate the virtual environment: .venv\Scripts\Activate.ps1"
Write-Host "2. Start AI Sidekick - run: uv run ai-sidekick --start"
Write-Host "3. Access web interface at http://localhost:8087"
Write-Host ""
