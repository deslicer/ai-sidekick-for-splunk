#!/bin/bash

# AI Sidekick for Splunk Lab - Restart Lab Setup Script (Unix/Linux/macOS)
# Combines stop and start operations for seamless restart

set -e

# Colors for output
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

# Welcome message
echo ""
echo "==========================================================="
echo "🔄 AI Sidekick for Splunk Lab - Restart AI Sidekick"
echo "   Google ADK + MCP + Splunk Integration"
echo "==========================================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1: Stop existing services
log_info "Stopping existing AI Sidekick services..."
if [ -f "$SCRIPT_DIR/stop-lab-setup.sh" ]; then
    bash "$SCRIPT_DIR/stop-lab-setup.sh"
else
    log_error "stop-lab-setup.sh not found in $SCRIPT_DIR"
    exit 1
fi

# Step 2: Wait a moment for services to fully stop
log_info "Waiting for services to fully stop..."
sleep 3

# Step 3: Start services again
log_info "Starting AI Sidekick services..."
if [ -f "$SCRIPT_DIR/start-lab-setup.sh" ]; then
    bash "$SCRIPT_DIR/start-lab-setup.sh"
else
    log_error "start-lab-setup.sh not found in $SCRIPT_DIR"
    exit 1
fi

echo ""
echo "==========================================================="
echo "🎉 AI Sidekick Restart Complete!"
echo "==========================================================="
echo ""
log_success "✅ Services stopped and restarted successfully"
echo ""
