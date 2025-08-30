# AI Sidekick for Splunk Lab - Restart Lab Setup Script (Windows PowerShell)
# Combines stop and start operations for seamless restart

# Colors for output (PowerShell compatible)
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
Write-Host "🔄 AI Sidekick for Splunk Lab - Restart AI Sidekick" -ForegroundColor Cyan
Write-Host "   Google ADK + MCP + Splunk Integration" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Step 1: Stop existing services
Write-Info "Stopping existing AI Sidekick services..."
$StopScript = Join-Path $ScriptDir "stop-lab-setup.ps1"
if (Test-Path $StopScript) {
    & $StopScript
} else {
    Write-Error "stop-lab-setup.ps1 not found in $ScriptDir"
    exit 1
}

# Step 2: Wait a moment for services to fully stop
Write-Info "Waiting for services to fully stop..."
Start-Sleep -Seconds 3

# Step 3: Start services again
Write-Info "Starting AI Sidekick services..."
$StartScript = Join-Path $ScriptDir "start-lab-setup.ps1"
if (Test-Path $StartScript) {
    & $StartScript
} else {
    Write-Error "start-lab-setup.ps1 not found in $ScriptDir"
    exit 1
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "🎉 AI Sidekick Restart Complete!" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Success "✅ Services stopped and restarted successfully"
Write-Host ""
