#!/bin/bash

# Switch Orchestrator Mode Script
# Switches between lab and production orchestrator prompts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ORCHESTRATOR_FILE="$PROJECT_ROOT/src/ai_sidekick_for_splunk/core/orchestrator.py"

# Function to show usage
show_usage() {
    echo -e "${BLUE}🎯 Orchestrator Mode Switcher${NC}"
    echo ""
    echo "Usage: $0 [lab|production|status]"
    echo ""
    echo "Commands:"
    echo -e "  ${YELLOW}lab${NC}        - Switch to lab mode (IndexAnalyzer only, no DataExplorer)"
    echo -e "  ${YELLOW}production${NC} - Switch to production mode (all agents including DataExplorer)"
    echo -e "  ${YELLOW}status${NC}     - Show current mode"
    echo ""
    echo "Lab mode removes DataExplorer agent to avoid confusion with IndexAnalyzer during workshops."
}

# Function to check current mode
check_current_mode() {
    if grep -q "orchestrator_prompt_lab" "$ORCHESTRATOR_FILE"; then
        echo "lab"
    else
        echo "production"
    fi
}

# Function to show current status
show_status() {
    local current_mode=$(check_current_mode)
    echo -e "${BLUE}🎯 Current Orchestrator Mode:${NC}"
    echo ""
    if [ "$current_mode" = "lab" ]; then
        echo -e "  Mode: ${YELLOW}LAB${NC}"
        echo -e "  Agents: search_guru, researcher, splunk_mcp, ${GREEN}IndexAnalyzer${NC}"
        echo -e "  Status: ${GREEN}✅ Simplified for workshops${NC}"
    else
        echo -e "  Mode: ${YELLOW}PRODUCTION${NC}"
        echo -e "  Agents: search_guru, researcher, splunk_mcp, DataExplorer, ${GREEN}IndexAnalyzer${NC}"
        echo -e "  Status: ${GREEN}✅ Full agent suite${NC}"
    fi
    echo ""
}

# Function to switch to lab mode
switch_to_lab() {
    echo -e "${BLUE}🔄 Switching to LAB mode...${NC}"

    # Backup current file
    cp "$ORCHESTRATOR_FILE" "$ORCHESTRATOR_FILE.backup"

    # Replace the import statement
    sed -i.tmp 's/from \.orchestrator_prompt import ORCHESTRATOR_INSTRUCTIONS/from .orchestrator_prompt_lab import ORCHESTRATOR_INSTRUCTIONS_LAB as ORCHESTRATOR_INSTRUCTIONS/' "$ORCHESTRATOR_FILE"
    sed -i.tmp 's/from \.orchestrator_prompt import ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS/from .orchestrator_prompt_lab import ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS_LAB as ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS/' "$ORCHESTRATOR_FILE"

    # Clean up temp file
    rm -f "$ORCHESTRATOR_FILE.tmp"

    echo -e "${GREEN}✅ Switched to LAB mode${NC}"
    echo ""
    echo -e "${YELLOW}Lab Mode Features:${NC}"
    echo -e "  • ${GREEN}IndexAnalyzer agent${NC} - For systematic index analysis"
    echo -e "  • ${GREEN}search_guru agent${NC} - For SPL optimization"
    echo -e "  • ${GREEN}researcher agent${NC} - For information research"
    echo -e "  • ${GREEN}splunk_mcp agent${NC} - For live Splunk operations"
    echo -e "  • ${RED}DataExplorer removed${NC} - Eliminates confusion with IndexAnalyzer"
    echo ""
    echo -e "${BLUE}💡 Perfect for workshops where participants focus on IndexAnalyzer!${NC}"
}

# Function to switch to production mode
switch_to_production() {
    echo -e "${BLUE}🔄 Switching to PRODUCTION mode...${NC}"

    # Backup current file
    cp "$ORCHESTRATOR_FILE" "$ORCHESTRATOR_FILE.backup"

    # Replace the import statement back to original
    sed -i.tmp 's/from \.orchestrator_prompt_lab import ORCHESTRATOR_INSTRUCTIONS_LAB as ORCHESTRATOR_INSTRUCTIONS/from .orchestrator_prompt import ORCHESTRATOR_INSTRUCTIONS/' "$ORCHESTRATOR_FILE"
    sed -i.tmp 's/from \.orchestrator_prompt_lab import ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS_LAB as ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS/from .orchestrator_prompt import ORCHESTRATOR_INSTRUCTIONS_NO_TOOLS/' "$ORCHESTRATOR_FILE"

    # Clean up temp file
    rm -f "$ORCHESTRATOR_FILE.tmp"

    echo -e "${GREEN}✅ Switched to PRODUCTION mode${NC}"
    echo ""
    echo -e "${YELLOW}Production Mode Features:${NC}"
    echo -e "  • ${GREEN}All agents available${NC} - Full agent suite"
    echo -e "  • ${GREEN}DataExplorer agent${NC} - For comprehensive data exploration"
    echo -e "  • ${GREEN}IndexAnalyzer agent${NC} - For systematic index analysis"
    echo -e "  • ${GREEN}search_guru agent${NC} - For SPL optimization"
    echo -e "  • ${GREEN}researcher agent${NC} - For information research"
    echo -e "  • ${GREEN}splunk_mcp agent${NC} - For live Splunk operations"
    echo ""
    echo -e "${BLUE}💡 Full feature set for production environments!${NC}"
}

# Main script logic
case "${1:-}" in
    "lab")
        switch_to_lab
        echo ""
        echo -e "${YELLOW}🔄 Next Steps:${NC}"
        echo -e "  1. Restart the lab environment: ${GREEN}./scripts/lab/start-lab-setup.sh${NC}"
        echo -e "  2. Test with: ${GREEN}'Use IndexAnalyzer to analyze index=pas'${NC}"
        ;;
    "production")
        switch_to_production
        echo ""
        echo -e "${YELLOW}🔄 Next Steps:${NC}"
        echo -e "  1. Restart the lab environment: ${GREEN}./scripts/lab/start-lab-setup.sh${NC}"
        echo -e "  2. Test with both agents available"
        ;;
    "status")
        show_status
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
