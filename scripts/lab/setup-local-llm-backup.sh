#!/bin/bash

# Local LLM Backup Setup for Workshops
# This script sets up Ollama as a backup for Google AI Studio
# Useful when API keys are unavailable or rate limits are exceeded

set -e

echo "🚀 Setting up Local LLM Backup for Workshop"
echo "============================================="

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is already installed"
    OLLAMA_INSTALLED=true
else
    echo "📦 Installing Ollama..."
    OLLAMA_INSTALLED=false
fi

# Install Ollama if not present
if [ "$OLLAMA_INSTALLED" = false ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍎 Detected macOS - Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "🐧 Detected Linux - Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo "❌ Unsupported OS. Please install Ollama manually from https://ollama.ai/"
        exit 1
    fi
fi

# Start Ollama service
echo "🔄 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!
sleep 5

# Pull recommended models for workshop
echo "📥 Downloading workshop-optimized models..."

# Lightweight model for basic tasks
echo "   📦 Pulling llama3.2:1b (lightweight, fast responses)..."
ollama pull llama3.2:1b

# Medium model for better quality
echo "   📦 Pulling llama3.2:3b (balanced performance)..."
ollama pull llama3.2:3b

# Code-focused model for Splunk queries
echo "   📦 Pulling codellama:7b-code (SPL optimization)..."
ollama pull codellama:7b-code

echo "✅ Local LLM models downloaded successfully!"

# Test the installation
echo "🧪 Testing local LLM setup..."
TEST_RESPONSE=$(ollama run llama3.2:1b "Hello! This is a test message for workshop validation." --format json 2>/dev/null || echo "")

if [[ -n "$TEST_RESPONSE" ]]; then
    echo "✅ Local LLM is working correctly!"
else
    echo "⚠️  Local LLM test failed, but installation completed"
fi

# Create workshop configuration for local LLM
echo "📝 Creating local LLM configuration..."

cat > local-llm-config.env << EOF
# Local LLM Configuration for Workshop Backup
OLLAMA_BASE_URL=http://localhost:11434/api
OLLAMA_MODEL_FAST=llama3.2:1b
OLLAMA_MODEL_BALANCED=llama3.2:3b
OLLAMA_MODEL_CODE=codellama:7b-code

# Usage instructions:
# - Use OLLAMA_MODEL_FAST for quick responses and basic tasks
# - Use OLLAMA_MODEL_BALANCED for better quality analysis
# - Use OLLAMA_MODEL_CODE for SPL query optimization
EOF

# Create a simple test script
cat > test-local-llm.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for local LLM backup system
"""

import requests
import json
import os

def test_ollama_connection():
    """Test connection to local Ollama instance"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running")
            print(f"📦 Available models: {len(models.get('models', []))}")
            for model in models.get('models', []):
                print(f"   - {model['name']}")
            return True
        else:
            print(f"❌ Ollama connection failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama connection error: {e}")
        return False

def test_model_generation(model_name="llama3.2:1b"):
    """Test model generation capability"""
    try:
        payload = {
            "model": model_name,
            "prompt": "Hello! This is a test for workshop backup system.",
            "stream": False
        }

        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Model {model_name} is working")
            print(f"📝 Response: {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ Model {model_name} test failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model {model_name} test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Local LLM Backup System")
    print("=" * 40)

    if test_ollama_connection():
        print("\n🔄 Testing model generation...")
        test_model_generation("llama3.2:1b")

        print("\n💡 Local LLM backup is ready!")
        print("   To use in workshop:")
        print("   1. Update .env with OLLAMA_BASE_URL=http://localhost:11434/api")
        print("   2. Switch model configuration to use local models")
        print("   3. Restart the AI Sidekick application")
    else:
        print("\n❌ Local LLM backup setup incomplete")
        print("   Please check Ollama installation and try again")
EOF

chmod +x test-local-llm.py

# Create workshop switching script
cat > switch-to-local-llm.sh << 'EOF'
#!/bin/bash

# Switch workshop to use local LLM backup

echo "🔄 Switching to Local LLM Backup Mode"
echo "====================================="

# Backup current .env
if [ -f "../../.env" ]; then
    cp "../../.env" "../../.env.backup.$(date +%Y%m%d-%H%M%S)"
    echo "💾 Backed up current .env file"
fi

# Update .env for local LLM
echo "📝 Updating environment configuration..."

# Add/update Ollama configuration
if grep -q "OLLAMA_BASE_URL" "../../.env" 2>/dev/null; then
    sed -i.bak 's|^OLLAMA_BASE_URL=.*|OLLAMA_BASE_URL=http://localhost:11434/api|' "../../.env"
else
    echo "OLLAMA_BASE_URL=http://localhost:11434/api" >> "../../.env"
fi

# Comment out other API keys to force local usage
sed -i.bak 's/^GOOGLE_API_KEY=/#GOOGLE_API_KEY=/' "../../.env" 2>/dev/null || true
sed -i.bak 's/^OPENAI_API_KEY=/#OPENAI_API_KEY=/' "../../.env" 2>/dev/null || true
sed -i.bak 's/^ANTHROPIC_API_KEY=/#ANTHROPIC_API_KEY=/' "../../.env" 2>/dev/null || true

echo "✅ Environment configured for local LLM"
echo "🔄 Please restart the AI Sidekick application"
echo ""
echo "💡 To switch back to cloud APIs:"
echo "   1. Restore from .env.backup.* file"
echo "   2. Or uncomment the API key lines in .env"
EOF

chmod +x switch-to-local-llm.sh

# Create restoration script
cat > switch-to-cloud-apis.sh << 'EOF'
#!/bin/bash

# Switch back to cloud APIs from local LLM

echo "🌐 Switching back to Cloud APIs"
echo "==============================="

# Find the most recent backup
BACKUP_FILE=$(ls -t ../../.env.backup.* 2>/dev/null | head -n1)

if [ -n "$BACKUP_FILE" ]; then
    cp "$BACKUP_FILE" "../../.env"
    echo "✅ Restored .env from backup: $(basename $BACKUP_FILE)"
else
    echo "⚠️  No backup found. Manually uncomment API keys in .env"
    echo "   Example:"
    echo "   #GOOGLE_API_KEY=your_key → GOOGLE_API_KEY=your_key"
fi

echo "🔄 Please restart the AI Sidekick application"
EOF

chmod +x switch-to-cloud-apis.sh

# Final instructions
echo ""
echo "🎉 Local LLM Backup Setup Complete!"
echo "===================================="
echo ""
echo "📁 Created files:"
echo "   - local-llm-config.env (configuration reference)"
echo "   - test-local-llm.py (test script)"
echo "   - switch-to-local-llm.sh (switch to local mode)"
echo "   - switch-to-cloud-apis.sh (switch back to cloud)"
echo ""
echo "🧪 Test the setup:"
echo "   python test-local-llm.py"
echo ""
echo "🔄 During workshop emergencies:"
echo "   ./switch-to-local-llm.sh"
echo ""
echo "💡 Model recommendations:"
echo "   - llama3.2:1b: Fast responses, basic tasks"
echo "   - llama3.2:3b: Better quality, balanced performance"
echo "   - codellama:7b-code: SPL optimization and code tasks"
echo ""
echo "⚠️  Note: Local models may have different response quality"
echo "   compared to cloud APIs, but provide reliable backup."

# Keep Ollama running in background
echo ""
echo "🔄 Ollama service is running in background (PID: $OLLAMA_PID)"
echo "   To stop: kill $OLLAMA_PID"
echo "   To restart: ollama serve &"
