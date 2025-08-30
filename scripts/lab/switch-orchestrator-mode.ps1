# Switch Orchestrator Mode Script (PowerShell)
# Switches between lab and production orchestrator prompts

param(
    [Parameter(Position=0)]
    [ValidateSet("lab", "production", "status", "")]
    [string]$Mode = ""
)

# Script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$OrchestratorFile = Join-Path $ProjectRoot "src\ai_sidekick_for_splunk\core\orchestrator.py"

# Function to show usage
function Show-Usage {
    Write-Host "🎯 Orchestrator Mode Switcher" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Usage: .\switch-orchestrator-mode.ps1 [lab|production|status]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  lab        - Switch to lab mode (IndexAnalyzer only, no DataExplorer)" -ForegroundColor Yellow
    Write-Host "  production - Switch to production mode (all agents including DataExplorer)" -ForegroundColor Yellow
    Write-Host "  status     - Show current mode" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Lab mode removes DataExplorer agent to avoid confusion with IndexAnalyzer during workshops."
}

# Function to check current mode
function Get-CurrentMode {
    $content = Get-Content $OrchestratorFile -Raw
    if ($content -match "orchestrator_prompt_lab") {
        return "lab"
    } else {
        return "production"
    }
}

# Function to show current status
function Show-Status {
    $currentMode = Get-CurrentMode
    Write-Host "🎯 Current Orchestrator Mode:" -ForegroundColor Blue
    Write-Host ""
    if ($currentMode -eq "lab") {
        Write-Host "  Mode: LAB" -ForegroundColor Yellow
        Write-Host "  Agents: search_guru, researcher, splunk_mcp, IndexAnalyzer" -ForegroundColor Green
        Write-Host "  Status: ✅ Simplified for workshops" -ForegroundColor Green
    } else {
        Write-Host "  Mode: PRODUCTION" -ForegroundColor Yellow
        Write-Host "  Agents: search_guru, researcher, splunk_mcp, DataExplorer, IndexAnalyzer" -ForegroundColor Green
        Write-Host "  Status: ✅ Full agent suite" -ForegroundColor Green
    }
    Write-Host ""
}

# Function to switch to lab mode
function Switch-ToLab {
    Write-Host "🔄 Switching to LAB mode..." -ForegroundColor Blue

    # Backup current file
    Copy-Item $OrchestratorFile "$OrchestratorFile.backup"

    # Replace the import statements
    $content = Get-Content $OrchestratorFile -Raw
    $content = $content -replace "from \.orchestrator_prompt import ORCHESTRATOR_INSTRUCTIONS", "from .orchestrator_prompt_lab import ORCHESTRATOR_INSTRUCTIONS_LAB as ORCHESTRATOR_INSTRUCTIONS"
    $content = $content -replace "from \.orchestrator_prompt import ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS", "from .orchestrator_prompt_lab import ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS_LAB as ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS"
    Set-Content $OrchestratorFile $content

    Write-Host "✅ Switched to LAB mode" -ForegroundColor Green
    Write-Host ""
    Write-Host "Lab Mode Features:" -ForegroundColor Yellow
    Write-Host "  • IndexAnalyzer agent - For systematic index analysis" -ForegroundColor Green
    Write-Host "  • search_guru agent - For SPL optimization" -ForegroundColor Green
    Write-Host "  • researcher agent - For information research" -ForegroundColor Green
    Write-Host "  • splunk_mcp agent - For live Splunk operations" -ForegroundColor Green
    Write-Host "  • DataExplorer removed - Eliminates confusion with IndexAnalyzer" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Perfect for workshops where participants focus on IndexAnalyzer!" -ForegroundColor Blue
}

# Function to switch to production mode
function Switch-ToProduction {
    Write-Host "🔄 Switching to PRODUCTION mode..." -ForegroundColor Blue

    # Backup current file
    Copy-Item $OrchestratorFile "$OrchestratorFile.backup"

    # Replace the import statements back to original
    $content = Get-Content $OrchestratorFile -Raw
    $content = $content -replace "from \.orchestrator_prompt_lab import ORCHESTRATOR_INSTRUCTIONS_LAB as ORCHESTRATOR_INSTRUCTIONS", "from .orchestrator_prompt import ORCHESTRATOR_INSTRUCTIONS"
    $content = $content -replace "from \.orchestrator_prompt_lab import ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS_LAB as ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS", "from .orchestrator_prompt import ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS"
    Set-Content $OrchestratorFile $content

    Write-Host "✅ Switched to PRODUCTION mode" -ForegroundColor Green
    Write-Host ""
    Write-Host "Production Mode Features:" -ForegroundColor Yellow
    Write-Host "  • All agents available - Full agent suite" -ForegroundColor Green
    Write-Host "  • DataExplorer agent - For comprehensive data exploration" -ForegroundColor Green
    Write-Host "  • IndexAnalyzer agent - For systematic index analysis" -ForegroundColor Green
    Write-Host "  • search_guru agent - For SPL optimization" -ForegroundColor Green
    Write-Host "  • researcher agent - For information research" -ForegroundColor Green
    Write-Host "  • splunk_mcp agent - For live Splunk operations" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Full feature set for production environments!" -ForegroundColor Blue
}

# Main script logic
switch ($Mode) {
    "lab" {
        Switch-ToLab
        Write-Host ""
        Write-Host "🔄 Next Steps:" -ForegroundColor Yellow
        Write-Host "  1. Restart the lab environment: .\scripts\lab\start-lab-setup.ps1" -ForegroundColor Green
        Write-Host "  2. Test with: 'Use IndexAnalyzer to analyze index=pas'" -ForegroundColor Green
    }
    "production" {
        Switch-ToProduction
        Write-Host ""
        Write-Host "🔄 Next Steps:" -ForegroundColor Yellow
        Write-Host "  1. Restart the lab environment: .\scripts\lab\start-lab-setup.ps1" -ForegroundColor Green
        Write-Host "  2. Test with both agents available" -ForegroundColor Green
    }
    "status" {
        Show-Status
    }
    default {
        Show-Usage
        exit 1
    }
}
