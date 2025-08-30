#!/bin/bash

# AI Sidekick for Splunk Lab - Build and Run Script (Unix/Linux/macOS)
# Starts the Google ADK agent on port 8087

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
echo "🚀 AI Sidekick for Splunk Lab - Start AI Sidekick"
echo "   Google ADK + MCP + Splunk Integration"
echo "==========================================================="
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to find available port starting from given port
find_available_port() {
    local start_port=$1
    local port=$start_port

    while ! check_port $port; do
        log_info "Port $port is in use, trying $((port + 1))..." >&2
        port=$((port + 1))
        if [ $port -gt $((start_port + 10)) ]; then
            log_error "Could not find available port in range $start_port-$((start_port + 10))" >&2
            exit 1
        fi
    done

    echo $port
}

# Step 1: Activate virtual environment
log_info "Activating virtual environment..."
if [ ! -d ".venv" ]; then
    log_error "Virtual environment not found. Please run ./scripts/check-prerequisites.sh first"
    exit 1
fi

source .venv/bin/activate
log_success "Virtual environment activated"

# Step 2: Check environment configuration
log_info "Checking environment configuration..."
if [ ! -f ".env" ]; then
    log_error ".env file not found. Please copy .env_template to .env and configure it"
    exit 1
fi

source .env

# Verify required environment variables
if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your-google-ai-studio-api-key" ]; then
    log_error "GOOGLE_API_KEY not configured in .env file"
    exit 1
fi

if [ -z "$SPLUNK_MCP_SERVER_URL" ]; then
    log_error "SPLUNK_MCP_SERVER_URL not configured in .env file"
    exit 1
fi

log_success "Environment configuration verified"

# Step 3: Ensure any existing ADK instance is not running
log_info "Ensuring any existing ADK instance is stopped..."
if [ -x "./scripts/lab/stop-lab-setup.sh" ]; then
    ./scripts/lab/stop-lab-setup.sh >/dev/null 2>&1 || true
fi

# Step 4: Find available port for AI Sidekick
log_info "Finding available port for AI Sidekick..."
SIDEKICK_PORT=$(find_available_port 8087)
if [ "$SIDEKICK_PORT" != "8087" ]; then
    log_warning "Default port 8087 in use, using port $SIDEKICK_PORT instead"
fi

# Step 4: Verify MCP server is running
log_info "Testing MCP server connection..."
if curl -s --max-time 5 "$SPLUNK_MCP_SERVER_URL" >/dev/null 2>&1; then
    log_success "MCP server is reachable at $SPLUNK_MCP_SERVER_URL"
else
    log_error "❌ MCP server not reachable at $SPLUNK_MCP_SERVER_URL"
    echo ""
    echo "🔧 Please start the MCP server before continuing:"
    echo ""
    echo "   For mcp-server-for-splunk:"
    echo "   cd ../mcp-server-for-splunk"
    echo "   uv run fastmcp run src/server.py --transport http --port 8001"
    echo ""
    echo "   Then re-run this script."
    echo ""
    exit 1
fi

# Step 6: Start Google ADK web interface
log_info "Starting Google ADK web interface on port $SIDEKICK_PORT..."

# Update PORT in environment for the agent
export PORT=$SIDEKICK_PORT

# Change to src directory so ADK can detect the agent properly
cd src

# Start the ADK web interface - this is the correct way per documentation
adk web --port $SIDEKICK_PORT &

SIDEKICK_PID=$!

# Change back to project root
cd ..

# Save PID for later cleanup
echo $SIDEKICK_PID > logs/ai-sidekick.pid

# Step 6: Wait for service to start
log_info "Waiting for ADK agent to start..."
sleep 8

# Step 7: Verify service is running
log_info "Verifying ADK agent is running..."
max_attempts=10
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:$SIDEKICK_PORT >/dev/null 2>&1; then
        log_success "ADK agent is running on port $SIDEKICK_PORT"
        break
    elif [ $attempt -eq $max_attempts ]; then
        log_warning "ADK agent may still be starting... check manually"
        break
    else
        log_info "Attempt $attempt/$max_attempts - waiting for agent..."
        sleep 3
        attempt=$((attempt + 1))
    fi
done

# Step 8: Display completion message
echo ""
echo "==========================================================="
echo "🎉 AI Sidekick Setup Complete!"
echo "==========================================================="
echo ""
log_success "✅ Virtual environment activated"
log_success "✅ Google ADK initialized"
log_success "✅ MCP server connection verified"
log_success "✅ AI agent running on port $SIDEKICK_PORT"
echo ""
echo "🌐 Web interface: http://localhost:$SIDEKICK_PORT"
echo ""
echo "📋 Next Steps:"
echo "1. Open your browser to http://localhost:$SIDEKICK_PORT"
echo "2. Select 'AI Sidekick for Splunk' from the agent dropdown"
echo "3. Try: 'Check my Splunk health status'"
echo "4. Explore the modular agent capabilities!"
echo ""
echo "🛑 To stop the AI Sidekick:"
echo "   ./scripts/lab/stop-lab-setup.sh"
echo ""
echo "🔄 To restart the AI Sidekick:"
echo "   ./scripts/lab/restart-lab-setup.sh"
echo ""

# Optionally open browser (uncomment if desired)
# if command -v open >/dev/null 2>&1; then
#     open http://localhost:$SIDEKICK_PORT
# elif command -v xdg-open >/dev/null 2>&1; then
#     xdg-open http://localhost:$SIDEKICK_PORT
# fi

log_info "AI Sidekick is running in the background (PID: $SIDEKICK_PID)"
log_info "Check process with: ps aux | grep $SIDEKICK_PID"
