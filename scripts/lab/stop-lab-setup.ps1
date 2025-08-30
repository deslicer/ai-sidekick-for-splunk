# Stop AI Sidekick and MCP Server services

$ProjectDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message"
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

Write-Host "Stopping AI Sidekick for Splunk services..."

# Stop AI Sidekick
$aiSidekickPidFile = Join-Path $ProjectDir "logs\ai-sidekick.pid"
if (Test-Path $aiSidekickPidFile) {
    $pid = Get-Content $aiSidekickPidFile
    try {
        Stop-Process -Id $pid -Force
        Write-Success "AI Sidekick stopped (PID: $pid)"
    } catch {
        Write-Info "AI Sidekick process not found or already stopped"
    }
    Remove-Item $aiSidekickPidFile -ErrorAction SilentlyContinue
}

# Stop MCP Server
$mcpPidFile = Join-Path $ProjectDir "logs\mcp-server.pid"
if (Test-Path $mcpPidFile) {
    $pid = Get-Content $mcpPidFile
    try {
        Stop-Process -Id $pid -Force
        Write-Success "MCP Server stopped (PID: $pid)"
    } catch {
        Write-Info "MCP Server process not found or already stopped"
    }
    Remove-Item $mcpPidFile -ErrorAction SilentlyContinue
}

# Kill any remaining ADK processes
Get-Process | Where-Object { $_.ProcessName -like "*adk*" -or $_.CommandLine -like "*adk web*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process | Where-Object { $_.ProcessName -eq "uvicorn" } | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process | Where-Object { $_.CommandLine -like "*ai_sidekick_for_splunk*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Kill any remaining processes on AI Sidekick port (8087)
try {
    Get-NetTCPConnection -LocalPort 8087 -ErrorAction SilentlyContinue | ForEach-Object {
        $processId = $_.OwningProcess
        try {
            Stop-Process -Id $processId -Force
            Write-Info "Stopped process on port 8087 (PID: $processId)"
        } catch {
            # Process may have already stopped
        }
    }
} catch {
    # Port may not be in use
}

Write-Success "AI Sidekick services stopped"
Write-Host ""
Write-Info "Note: MCP server (port 8001) is managed separately"
Write-Info "To stop MCP server, use its own stop commands or kill the process manually"

Write-Success "All services stopped"
