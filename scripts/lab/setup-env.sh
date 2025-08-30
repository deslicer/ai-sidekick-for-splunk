#!/bin/bash

# =============================================================================
# AI Sidekick for Splunk Lab Environment Setup Script
# =============================================================================
# Interactive script to create .env file with user-provided values

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEFAULT_MCP_URL="http://localhost:8003/mcp/"
DEFAULT_DOCKER_MCP_URL="http://mcp-server-modular:8001/mcp/"
DEFAULT_MODEL="gemini-2.0-flash-exp"
DEFAULT_PORT="8000"
DEFAULT_LOG_LEVEL="info"

echo -e "${BLUE}🚀 AI Sidekick for Splunk Lab Environment Setup${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Helper to read existing value from .env and strip surrounding quotes
get_env_value() {
    local key="$1"
    if [ -f .env ]; then
        local line
        line=$(grep -E "^${key}=" .env | head -n1 || true)
        if [ -n "$line" ]; then
            echo "${line#*=}" | sed -e 's/^\"//' -e 's/\"$//' -e "s/^'//" -e "s/'$//"
            return
        fi
    fi
    echo ""
}

# Check if .env already exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists!${NC}"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [[ ! $overwrite =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ Keeping existing .env file${NC}"
        exit 0
    fi
    echo ""
fi

echo -e "${GREEN}📝 Let's configure your workshop environment...${NC}"
echo ""

# Google API Key (Required)
echo -e "${BLUE}🔑 Google AI Studio Configuration${NC}"
echo "Get your API key from: https://aistudio.google.com/app/apikey"
WORKSHOP_CSV="internal/admin/workshop-management/workshop-participants.csv"
google_api_key=""
if [ -f "$WORKSHOP_CSV" ]; then
    read -p "Autogenerate Google API key for this workshop? (Y/n): " auto_choice
    auto_choice=${auto_choice:-Y}
    if [[ $auto_choice =~ ^[Yy]$ ]]; then
        suggested_key=$(awk -F, 'NR>1 && $3!="" {print $3}' "$WORKSHOP_CSV" | awk 'BEGIN{srand()} {a[NR]=$0} END{if (NR>0) print a[int(rand()*NR)+1]}')
        if [ -n "$suggested_key" ]; then
            echo -e "${GREEN}✅ Found a workshop key (masked): ****${suggested_key: -4}${NC}"
            read -s -p "Press Enter to accept or paste a different key: " input_key
            echo ""
            if [ -n "$input_key" ]; then
                google_api_key="$input_key"
            else
                google_api_key="$suggested_key"
            fi
        fi
    fi
fi
while true; do
    if [ -n "$google_api_key" ]; then
        # already set from CSV flow above
        :
    else
        read -s -p "Enter your Google AI Studio API key: " google_api_key
        echo ""
    fi
    if [ -n "$google_api_key" ] && [ "$google_api_key" != "your-google-ai-studio-api-key" ]; then
        break
    fi
    echo -e "${RED}❌ Please provide a valid Google API key${NC}"
done
echo ""

# MCP Server Configuration
echo -e "${BLUE}🔧 MCP Server Configuration${NC}"
default_mcp_url="$DEFAULT_MCP_URL"
read -p "MCP server URL [$default_mcp_url, press Enter to keep existing]: " mcp_url
mcp_url=${mcp_url:-$default_mcp_url}
echo ""

# Splunk Connection Configuration
echo -e "${BLUE}🔗 Splunk Connection Configuration${NC}"
echo "The MCP server needs to connect to your Splunk instance."
echo ""
echo "Default workshop Splunk instance: dev1666-i-035e95d7e4ea1c310.splunk.show"
read -p "Use workshop Splunk instance? (Y/n): " use_workshop_splunk
use_workshop_splunk=${use_workshop_splunk:-Y}

if [[ $use_workshop_splunk =~ ^[Yy]$ ]]; then
    splunk_host="dev1666-i-035e95d7e4ea1c310.splunk.show"
    splunk_port="8089"
    splunk_scheme="https"
    splunk_username="admin"
    splunk_verify_ssl="true"
    echo -e "${GREEN}✅ Using workshop Splunk instance${NC}"
else
    read -p "Splunk host [press Enter to keep existing if present]: " splunk_host
    read -p "Splunk port [8089, press Enter to keep existing if present]: " splunk_port
    splunk_port=${splunk_port:-8089}
    read -p "Splunk scheme (http/https) [https, press Enter to keep existing if present]: " splunk_scheme
    splunk_scheme=${splunk_scheme:-https}
    read -p "Splunk username [admin, press Enter to keep existing if present]: " splunk_username
    splunk_username=${splunk_username:-admin}
    read -p "Verify SSL certificates? (true/false) [true, press Enter to keep existing if present]: " splunk_verify_ssl
    splunk_verify_ssl=${splunk_verify_ssl:-true}
fi

# Always prompt for password (security) with support for keeping existing
echo ""
existing_pw=$(get_env_value SPLUNK_PASSWORD)
if [ -n "$existing_pw" ]; then
    read -s -p "Splunk password [press Enter to keep existing]: " splunk_password
    echo ""
    if [ -z "$splunk_password" ]; then splunk_password="$existing_pw"; fi
else
    read -s -p "Splunk password: " splunk_password
    echo ""
fi
echo -e "${GREEN}✅ Splunk connection configured${NC}"
echo ""

# Model Configuration
echo -e "${BLUE}🤖 Model Configuration${NC}"
read -p "LLM Model [$DEFAULT_MODEL, press Enter to keep existing if present]: " model
model=${model:-$DEFAULT_MODEL}
echo -e "${GREEN}✅ Using model: $model${NC}"
echo ""

# Server Configuration
echo -e "${BLUE}🌐 Server Configuration${NC}"
read -p "Server port [$DEFAULT_PORT, press Enter to keep existing if present]: " port
port=${port:-$DEFAULT_PORT}

read -p "Log level [$DEFAULT_LOG_LEVEL, press Enter to keep existing if present]: " log_level
log_level=${log_level:-$DEFAULT_LOG_LEVEL}
echo ""

# Create .env file
echo -e "${BLUE}📄 Creating .env file...${NC}"

# Escape single quotes for safe single-quoted env value
splunk_password_escaped=$(printf "%s" "$splunk_password" | sed "s/'/'\"'\"'/g")

cat > .env << EOF
# =============================================================================
# AI Sidekick for Splunk Lab Environment Configuration
# =============================================================================
# Generated by setup-env.sh on $(date)

# =============================================================================
# Google ADK Configuration (Required)
# =============================================================================
GOOGLE_GENAI_USE_VERTEXAI=False
GOOGLE_API_KEY=$google_api_key

# LLM Model Configuration
BASE_MODEL=$model
TUTOR_MODEL=$model

# =============================================================================
# MCP Server Configuration (Required for Splunk Integration)
# =============================================================================
SPLUNK_MCP_SERVER_URL=$mcp_url

# Splunk Connection Details (Required for MCP server)
SPLUNK_HOST='$splunk_host'
SPLUNK_PORT='$splunk_port'
SPLUNK_SCHEME='$splunk_scheme'
SPLUNK_USERNAME='$splunk_username'
SPLUNK_PASSWORD='$splunk_password_escaped'
SPLUNK_VERIFY_SSL='$splunk_verify_ssl'

# =============================================================================
# Core ADK Agent Configuration (Required)
# =============================================================================
ADK_AGENT_MODULE_PATH=src.backend.app.agent
ADK_AGENT_INSTANCE_NAME=root_agent

# =============================================================================
# Workshop Server Configuration
# =============================================================================
APP_NAME="AI Sidekick for Splunk"
DEBUG=false
HOST=0.0.0.0
PORT=$port
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=$port
LOG_LEVEL=$log_level



# =============================================================================
# Additional Configuration
# =============================================================================
VERSION=1.0.0
RELOAD=false
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
DEV_MODE=true
SHOW_DETAILED_ERRORS=true
EOF

echo -e "${GREEN}✅ .env file created successfully!${NC}"
echo ""

# Summary
echo -e "${BLUE}📋 Configuration Summary:${NC}"
echo -e "  Google API Key: ${GREEN}[CONFIGURED]${NC}"
echo -e "  MCP Server: ${GREEN}$mcp_url${NC}"
echo -e "  Splunk Host: ${GREEN}$splunk_host${NC}"
echo -e "  Splunk Port: ${GREEN}$splunk_port${NC}"
echo -e "  Splunk Scheme: ${GREEN}$splunk_scheme${NC}"
echo -e "  Splunk Username: ${GREEN}$splunk_username${NC}"
echo -e "  Splunk Verify SSL: ${GREEN}$splunk_verify_ssl${NC}"
if [ -n "$splunk_password" ]; then
  echo -e "  Splunk Password: ${GREEN}[CONFIGURED]${NC}"
else
  echo -e "  Splunk Password: ${YELLOW}[NOT SET]${NC}"
fi
echo -e "  Model: ${GREEN}$model${NC}"
echo -e "  Server Port: ${GREEN}$port${NC}"
echo -e "  Log Level: ${GREEN}$log_level${NC}"
echo ""

# Next steps
echo -e "${BLUE}🎯 Next Steps:${NC}"
if [[ $mcp_url == *"localhost"* ]]; then
    echo -e "  1. ${YELLOW}Start MCP server:${NC} cd mcp-server-for-splunk && ./scripts/build_and_run.sh"
else
    echo -e "  1. ${YELLOW}Start Docker services:${NC} docker-compose up -d"
fi
echo -e "  2. ${YELLOW}Start AI Sidekick:${NC} uv run start-lab"
echo -e "  3. ${YELLOW}Access workshop:${NC} http://localhost:8087"
echo ""

echo -e "${GREEN}🎉 Workshop environment setup complete!${NC}"
