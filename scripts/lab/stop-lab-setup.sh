#!/bin/bash

# Stop AI Sidekick and MCP Server services

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "[INFO] $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Stopping AI Sidekick for Splunk services..."

# Stop AI Sidekick
if [ -f "$PROJECT_DIR/logs/ai-sidekick.pid" ]; then
    PID=$(cat "$PROJECT_DIR/logs/ai-sidekick.pid")
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        log_success "AI Sidekick stopped (PID: $PID)"
    else
        log_info "AI Sidekick process not found"
    fi
    rm -f "$PROJECT_DIR/logs/ai-sidekick.pid"
fi

# Stop MCP Server
if [ -f "$PROJECT_DIR/logs/mcp-server.pid" ]; then
    PID=$(cat "$PROJECT_DIR/logs/mcp-server.pid")
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        log_success "MCP Server stopped (PID: $PID)"
    else
        log_info "MCP Server process not found"
    fi
    rm -f "$PROJECT_DIR/logs/mcp-server.pid"
fi

# Stop specific service PIDs if available
if [ -f "logs/ai-sidekick.pid" ]; then
    AI_PID=$(cat logs/ai-sidekick.pid 2>/dev/null)
    if [ ! -z "$AI_PID" ] && kill -0 "$AI_PID" 2>/dev/null; then
        kill "$AI_PID" 2>/dev/null
        log_info "Stopped AI Sidekick process (PID: $AI_PID)"
    fi
    rm -f logs/ai-sidekick.pid
fi

# Kill any remaining ADK processes
pkill -f "adk web" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "python.*ai_sidekick_for_splunk" 2>/dev/null || true

# Kill any remaining processes on AI Sidekick port
if command -v lsof >/dev/null 2>&1; then
    PIDS=$(lsof -ti:8087 2>/dev/null)
    if [ ! -z "$PIDS" ]; then
        echo $PIDS | xargs kill -9 2>/dev/null
        log_info "Stopped processes on port 8087"
    fi
fi

log_success "AI Sidekick services stopped"
echo ""
log_info "Note: MCP server (port 8001) is managed separately"
log_info "To stop MCP server, use its own stop commands or kill the process manually"

log_success "All services stopped"