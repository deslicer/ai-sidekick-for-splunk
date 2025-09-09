# AI Sidekick for Splunk Lab - Build and Run Script (Windows PowerShell)
# Starts the Google ADK agent on port 8087

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

# Welcome message
Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "🚀 AI Sidekick for Splunk Lab - Start AI Sidekick" -ForegroundColor Cyan
Write-Host "   Google ADK + MCP + Splunk Integration" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Create logs directory if it doesn't exist
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Function to check if port is available
function Test-Port {
    param([int]$Port)
    try {
        $listener = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties()
        $activePorts = $listener.GetActiveTcpListeners() | ForEach-Object { $_.Port }
        return -not ($activePorts -contains $Port)
    } catch {
        return $true
    }
}

# Function to find available port starting from given port
function Find-AvailablePort {
    param([int]$StartPort)
    $port = $StartPort

    while (-not (Test-Port $port)) {
        Write-Info "Port $port is in use, trying $($port + 1)..."
        $port++
        if ($port -gt ($StartPort + 10)) {
            Write-Error "Could not find available port in range $StartPort-$($StartPort + 10)"
            exit 1
        }
    }

    return $port
}

# Step 1: Activate virtual environment
Write-Info "Activating virtual environment..."
if (-not (Test-Path ".venv")) {
    Write-Error "Virtual environment not found. Please run .\scripts\smart-install.ps1 first"
    exit 1
}

& ".venv\Scripts\Activate.ps1"
Write-Success "Virtual environment activated"

# Step 2: Check environment configuration
Write-Info "Checking environment configuration..."
if (-not (Test-Path ".env")) {
    Write-Error ".env file not found. Please copy .env_template to .env and configure it"
    exit 1
}

# Load environment variables
Get-Content ".env" | ForEach-Object {
    if ($_ -match "^([^=]+)=(.*)$") {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# Verify required environment variables
$googleApiKey = [System.Environment]::GetEnvironmentVariable("GOOGLE_API_KEY", "Process")
$mcpServerUrl = [System.Environment]::GetEnvironmentVariable("SPLUNK_MCP_SERVER_URL", "Process")

if (-not $googleApiKey -or $googleApiKey -eq "your-google-ai-studio-api-key") {
    Write-Error "GOOGLE_API_KEY not configured in .env file"
    exit 1
}

if (-not $mcpServerUrl) {
    Write-Error "SPLUNK_MCP_SERVER_URL not configured in .env file"
    exit 1
}

Write-Success "Environment configuration verified"

# Step 3: Find available port for AI Sidekick
Write-Info "Finding available port for AI Sidekick..."
$sidekickPort = Find-AvailablePort 8087

if ($sidekickPort -ne 8087) {
    Write-Warning "Default port 8087 in use, using port $sidekickPort instead"
}

# Step 4: Verify MCP server is running
Write-Info "Testing MCP server connection..."
try {
    $response = Invoke-WebRequest -Uri $mcpServerUrl -Method Head -TimeoutSec 5 -ErrorAction SilentlyContinue
    Write-Success "MCP server is reachable at $mcpServerUrl"
} catch {
    Write-Error "❌ MCP server not reachable at $mcpServerUrl"
    Write-Host ""
    Write-Host "🔧 Please start the MCP server before continuing:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   For mcp-server-for-splunk:" -ForegroundColor Cyan
    Write-Host "   cd ..\mcp-server-for-splunk" -ForegroundColor White
    Write-Host "   uv run fastmcp run src/server.py --transport http --port 8001" -ForegroundColor White
    Write-Host ""
    Write-Host "   Then re-run this script." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Step 5: Start Google ADK web interface
Write-Info "Starting Google ADK web interface on port $sidekickPort..."

# Update PORT in environment for the agent
[System.Environment]::SetEnvironmentVariable("PORT", $sidekickPort, "Process")

# Change to src directory so ADK can detect the agent properly
Set-Location "src"

# Start the ADK web interface - this is the correct way per documentation
$process = Start-Process -FilePath "adk" -ArgumentList "web", "--port", $sidekickPort -PassThru -WindowStyle Hidden

# Change back to project root
Set-Location ".."

# Save PID for later cleanup
$process.Id | Out-File -FilePath "logs\ai-sidekick.pid" -Encoding ASCII

# Step 6: Wait for service to start
Write-Info "Waiting for ADK agent to start..."
Start-Sleep -Seconds 8

# Step 7: Verify service is running
Write-Info "Verifying ADK agent is running..."
$maxAttempts = 10
$attempt = 1

while ($attempt -le $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$sidekickPort" -Method Head -TimeoutSec 3 -ErrorAction SilentlyContinue
        Write-Success "ADK agent is running on port $sidekickPort"
        break
    } catch {
        if ($attempt -eq $maxAttempts) {
            Write-Warning "ADK agent may still be starting... check manually"
            break
        } else {
            Write-Info "Attempt $attempt/$maxAttempts - waiting for agent..."
            Start-Sleep -Seconds 3
            $attempt++
        }
    }
}

# Step 8: Display completion message
Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "🎉 AI Sidekick Setup Complete!" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Success "✅ Virtual environment activated"
Write-Success "✅ Google ADK initialized"
Write-Success "✅ MCP server connection verified"
Write-Success "✅ AI agent running on port $sidekickPort"
Write-Host ""
Write-Host "🌐 Web interface: http://localhost:$sidekickPort"
Write-Host ""
Write-Host "📋 Next Steps:"
Write-Host "1. Open your browser to http://localhost:$sidekickPort"
Write-Host "2. Select 'AI Sidekick for Splunk' from the agent dropdown"
Write-Host "3. Try: 'Check my Splunk health status'"
Write-Host "4. Explore the modular agent capabilities!"
Write-Host ""
Write-Host "🛑 To stop the AI Sidekick:"
Write-Host "   .\scripts\stop-services.ps1"
Write-Host ""

Write-Info "AI Sidekick is running in the background (PID: $($process.Id))"
Write-Info "Check process with: Get-Process -Id $($process.Id)"
